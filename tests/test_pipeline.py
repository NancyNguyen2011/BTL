"""Kiểm chứng các rủi ro chính: parsing, sai kỳ, khóa trùng, transaction và nguồn lỗi."""
import json
import sqlite3

import numpy as np
import pandas as pd
import pytest

from src.cleaner import clean_data, parse_number, read_raw
from src.config import RAW_DIR
from src.database import load_database, save_database
from src.pipeline import run_pipeline
from src.transformer import normalize_nav, trailing_returns, transform_data


@pytest.mark.parametrize("raw,expected", [('<span class="text-green">6,05</span>', 6.05),
                                         ("1.234,56", 1234.56), ("1,234.56", 1234.56), ("-0,21%", -.21)])
def test_number_formats(raw, expected):
    assert parse_number(raw) == pytest.approx(expected)


@pytest.mark.parametrize("raw", ["-", "", "bad", None, "inf"])
def test_missing_numbers_are_not_zero(raw):
    assert np.isnan(parse_number(raw))


def test_actual_data_quality_and_joins():
    clean = clean_data(read_raw())
    nav = clean["fund_nav"]
    assert len(nav) == 4843
    assert not nav.duplicated(["fund_id", "date"]).any()
    assert len(clean["rejected_rows"]) == 18
    assert nav.symbol.nunique() == 5
    assert len(clean["bank_rates"]) == 405
    assert clean["bank_rates"].annual_rate.isna().sum() > 0
    assert clean["macro_cpi"].cpi_mom.isna().sum() == 1
    bank = clean["bank_rates"]
    # Giữ nhãn nguồn, không dịch cột ngầm khi có nghi vấn.
    row = bank[(bank.bank_name == "Agribank") & (bank.term_months == 12)].iloc[0]
    assert row.annual_rate == 5.9
    assert row.unmapped_rate == .2


def test_normalization_and_year_aligned_return():
    nav = pd.DataFrame({"fund_id": [1, 1, 1], "date": pd.to_datetime(["2020-01-02", "2020-07-02", "2021-01-02"]), "nav": [200, 180, 220]})
    out = normalize_nav(nav)
    assert out.normalized_nav.tolist() == pytest.approx([100, 90, 110])
    assert out.drawdown.min() == pytest.approx(-10)
    trailing = trailing_returns(nav, 12)
    assert np.isnan(trailing.iloc[1])
    assert trailing.iloc[2] == pytest.approx(10)


def test_real_return_missing_history_and_cpi():
    tables = transform_data(clean_data(read_raw()))
    nav = tables["fund_nav"]
    assert nav.groupby("fund_id").first().normalized_nav.eq(100).all()
    assert nav[nav.date < "2021-01-01"].return_12m_nav.isna().all()
    row = nav.dropna(subset=["return_12m_nav", "cpi_yoy"]).iloc[-1]
    assert row.real_return_12m == pytest.approx(row.return_12m_nav - row.cpi_yoy)
    assert row.real_return_fisher_12m == pytest.approx(((1 + row.return_12m_nav / 100) / (1 + row.cpi_yoy / 100) - 1) * 100)


def test_pipeline_idempotence_and_atomic_rollback(tmp_path):
    path = tmp_path / "test.db"
    run = run_pipeline(db_path=path)
    run_pipeline(db_path=path)
    before = load_database(path)
    assert len(before["update_history"]) == 2
    assert len(before["fund_nav"]) == 4843
    tables = {k: v.copy() for k, v in before.items() if k != "update_history"}
    tables["fund_nav"] = pd.concat([tables["fund_nav"], tables["fund_nav"].iloc[[0]]])
    with pytest.raises(sqlite3.IntegrityError):
        save_database(tables, run, path)
    after = load_database(path)
    pd.testing.assert_frame_equal(before["fund_nav"], after["fund_nav"])
    assert len(after["update_history"]) == 2


def test_invalid_input_does_not_replace_database(tmp_path):
    path = tmp_path / "safe.db"
    run_pipeline(db_path=path)
    original = path.read_bytes()
    with pytest.raises(ValueError, match="Thiếu file"):
        run_pipeline(raw_dir=tmp_path / "missing", db_path=path)
    assert path.read_bytes() == original


def test_csv_endpoint_collection(tmp_path, monkeypatch):
    import io
    from src import scraper
    config = tmp_path / "sources.json"
    config.write_text(json.dumps({"csv_urls": {"fund_nav": "https://example.test/nav.csv"}}))
    monkeypatch.setattr(scraper, "urlopen", lambda *args, **kwargs: io.BytesIO((RAW_DIR / "raw_fund_nav_daily.csv").read_bytes()))
    result = run_pipeline(db_path=tmp_path / "remote.db", sources_config=config)
    assert "HTTPS" in result["mode"]
