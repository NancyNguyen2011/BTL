"""Stage 3: kiểm tra schema, làm sạch kiểu dữ liệu và kết hợp các bảng.

Tỷ lệ luôn tính bằng phần trăm (6.5 tức 6.5%), không phải phân số.
Không suy diễn ô thiếu thành 0 hoặc tự sửa nhãn kỳ hạn không có căn cứ.
"""
import html
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import FILES, RAW_DIR

REQUIRED = {
    "fund_info": ["fund_id", "symbol", "fund_name", "fund_type", "risk_level",
                  "buy_min_value", "management_fee", "owner_name", "return_1m",
                  "return_3m", "return_6m", "return_12m", "return_since_inception", "is_transferred"],
    "fund_nav": ["fund_id", "symbol", "navDate", "nav"],
    "fund_holdings": ["fund_id", "asset_type", "asset_percent", "update_date"],
    "bank_rates": ["bank_name", "deposit_type", "scrape_date", "web_update_time",
                   "06 tháng", "12 tháng", "24 tháng"],
    "macro_cpi": ["period_str", "cpi_yoy_str", "cpi_mom_str", "status"],
}


def clean_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>", "", html.unescape(str(value)))).strip()


def parse_number(value):
    """Hỗ trợ 6,05%; 1.234,56; 1,234.56 và dấu chấm thập phân."""
    text = clean_text(value).replace("%", "").replace(" ", "").replace("−", "-")
    if text.lower() in {"", "-", "--", "n/a", "nan", "none"}:
        return np.nan
    if "," in text and "." in text:
        text = (text.replace(".", "").replace(",", ".") if text.rfind(",") > text.rfind(".")
                else text.replace(",", ""))
    else:
        text = text.replace(",", ".")
    try:
        number = float(text)
        return number if np.isfinite(number) else np.nan
    except ValueError:
        return np.nan


def read_raw(raw_dir=RAW_DIR):
    """Đọc thành chuỗi để không mất dấu vết lỗi của bản nguồn."""
    tables = {}
    for name, filename in FILES.items():
        path = Path(raw_dir) / filename
        if not path.is_file():
            raise ValueError(f"Thiếu file dữ liệu: {path}")
        frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
        missing = set(REQUIRED[name]) - set(frame.columns)
        if missing:
            raise ValueError(f"{filename}: thiếu cột {sorted(missing)}")
        if frame.empty:
            raise ValueError(f"{filename}: không có dòng dữ liệu")
        tables[name] = frame
    return tables


def clean_data(raw):
    """Trả về bảng sạch và báo cáo chất lượng; dữ liệu khóa lỗi bị loại có thống kê."""
    tables, issues, rejected = {}, [], []

    def report(table, detail, count=1):
        issues.append({"table_name": table, "detail": detail, "count": int(count)})

    def finish(name, frame, required, keys):
        valid = frame.dropna(subset=required)
        report(name, "Dòng thiếu hoặc sai giá trị bắt buộc bị loại", len(frame) - len(valid))
        # Khóa trùng có số liệu mâu thuẫn: cách ly tất cả, không tùy tiện chọn một bản.
        valid = valid.drop_duplicates()
        report(name, "Dòng trùng hoàn toàn bị loại", len(frame.dropna(subset=required)) - len(valid))
        conflicts = valid.duplicated(keys, keep=False)
        invalid = frame[frame[required].isna().any(axis=1)]
        for reason, records in [("Giá trị bắt buộc thiếu/sai", invalid), ("Khóa trùng mâu thuẫn", valid[conflicts])]:
            for record in records.to_dict("records"):
                rejected.append({"table_name": name, "reason": reason,
                                 "record_json": json.dumps(record, ensure_ascii=False, default=str)})
        report(name, "Dòng khóa trùng mâu thuẫn được cách ly", conflicts.sum())
        valid = valid[~conflicts]
        if valid.empty:
            raise ValueError(f"{name}: không còn dữ liệu hợp lệ")
        return valid.reset_index(drop=True)

    info = raw["fund_info"].copy()
    for c in info.columns:
        info[c] = info[c].map(clean_text)
    for c in ["fund_id", "buy_min_value", "management_fee"] + [c for c in info if c.startswith("return_")]:
        info[c] = info[c].map(parse_number)
    info["symbol"] = info.symbol.replace("", np.nan)
    info["is_transferred"] = info.is_transferred.str.lower().map({"true": True, "false": False})
    info = finish("fund_info", info, ["fund_id", "symbol"], ["fund_id"])
    if info.symbol.duplicated().any():
        raise ValueError("Mã quỹ không duy nhất")
    tables["fund_info"] = info

    nav = raw["fund_nav"].rename(columns={"navDate": "date"}).copy()
    nav["fund_id"] = nav.fund_id.map(parse_number)
    nav["nav"] = nav.nav.map(parse_number)
    nav.loc[nav.nav <= 0, "nav"] = np.nan
    nav["date"] = pd.to_datetime(nav.date, format="%Y-%m-%d", errors="coerce")
    nav = finish("fund_nav", nav, ["fund_id", "date", "nav"], ["fund_id", "date"])
    joined = nav.merge(info[["fund_id", "symbol", "fund_type"]], on="fund_id",
                       how="left", suffixes=("_raw", ""), validate="many_to_one")
    if joined.symbol.isna().any() or (joined.symbol_raw != joined.symbol).any():
        raise ValueError("NAV có fund_id/mã quỹ không khớp danh mục quỹ")
    tables["fund_nav"] = joined.drop(columns="symbol_raw").sort_values(["fund_id", "date"])

    holdings = raw["fund_holdings"].copy()
    for c in ["fund_id", "asset_percent"]:
        holdings[c] = holdings[c].map(parse_number)
    holdings["asset_type"] = holdings.asset_type.map(clean_text).replace("", np.nan)
    holdings["update_date"] = pd.to_datetime(holdings.update_date, errors="coerce")
    holdings.loc[~holdings.asset_percent.between(0, 100), "asset_percent"] = np.nan
    holdings = finish("fund_holdings", holdings, list(holdings.columns),
                      ["fund_id", "asset_type", "update_date"])
    holdings = holdings.merge(info[["fund_id", "symbol"]], on="fund_id", how="left", validate="many_to_one")
    if holdings.symbol.isna().any():
        raise ValueError("Danh mục tài sản có quỹ không tồn tại")
    totals = holdings.groupby(["fund_id", "update_date"]).asset_percent.sum()
    report("fund_holdings", "Cơ cấu có tổng khác 100% (sai số > 0.1)", (~np.isclose(totals, 100, atol=.1)).sum())
    tables["fund_holdings"] = holdings

    bank = raw["bank_rates"].copy()
    # Cột không rõ kỳ hạn được lưu riêng để có thể kiểm toán, không sử dụng để tính toán.
    unknown = "Kỳ hạn gửi tiết kiệm (tháng)"
    if unknown in bank:
        bank["unmapped_rate"] = bank[unknown].map(parse_number)
        report("bank_rates", "Tiêu đề kỳ hạn có dấu hiệu lệch: giữ nhãn nguồn; cột không rõ kỳ hạn không dùng so sánh", len(bank))
    else:
        bank["unmapped_rate"] = np.nan
    for c in ["bank_name", "deposit_type"]:
        bank[c] = bank[c].map(clean_text).replace("", np.nan)
    for c in ["scrape_date", "web_update_time"]:
        bank[c] = pd.to_datetime(bank[c], errors="coerce")
    rate_cols = [c for c in bank if re.fullmatch(r"\d+ tháng", c) or c == "Không Kỳ Hạn"]
    bank = bank.melt(id_vars=["bank_name", "deposit_type", "scrape_date", "web_update_time", "unmapped_rate"],
                     value_vars=rate_cols, var_name="source_term_label", value_name="rate_raw")
    bank["term_months"] = bank.source_term_label.map(lambda s: int(s.split()[0]) if s[0].isdigit() else 0)
    bank["annual_rate"] = bank.rate_raw.map(parse_number)
    bank.loc[~bank.annual_rate.between(0, 100), "annual_rate"] = np.nan
    report("bank_rates", "Lãi suất thiếu/sai: giữ NULL và bỏ khỏi phép so sánh", bank.annual_rate.isna().sum())
    tables["bank_rates"] = finish("bank_rates", bank, ["bank_name", "deposit_type", "scrape_date"],
                                  ["bank_name", "deposit_type", "term_months", "scrape_date"])

    cpi = raw["macro_cpi"].copy()
    parts = cpi.period_str.str.extract(r"(\d{1,2})/(\d{4})")
    cpi["date"] = pd.to_datetime(parts[1] + "-" + parts[0] + "-01", errors="coerce")
    cpi["cpi_yoy"] = cpi.cpi_yoy_str.map(parse_number)
    cpi["cpi_mom"] = cpi.cpi_mom_str.map(parse_number)
    cpi["status"] = cpi.status.map(clean_text)
    report("macro_cpi", "CPI MoM thiếu; không thể dựng chỉ số giá tích lũy đầy đủ", cpi.cpi_mom.isna().sum())
    tables["macro_cpi"] = finish("macro_cpi", cpi, ["date", "cpi_yoy"], ["date"]).sort_values("date")
    tables["quality_report"] = pd.DataFrame(issues)
    tables["rejected_rows"] = pd.DataFrame(rejected, columns=["table_name", "reason", "record_json"])
    return tables
