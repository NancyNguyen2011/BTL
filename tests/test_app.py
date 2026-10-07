"""Chạy Streamlit thật bằng AppTest và thao tác các nhánh bộ lọc quan trọng."""
import datetime as dt

from streamlit.testing.v1 import AppTest

from src.config import ROOT


def find(elements, label):
    return next(item for item in elements if item.label == label)


def test_dashboard_interactions():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not at.exception
    assert len(at.tabs) == 4
    find(at.selectbox, "Loại quỹ").select("Quỹ trái phiếu").run()
    assert not at.exception
    find(at.selectbox, "Kỳ hạn ngân hàng (tháng)").select(24).run()
    assert not at.exception
    find(at.multiselect, "Ngân hàng so sánh").set_value([]).run()
    assert not at.exception
    find(at.slider, "Khoảng thời gian").set_value((dt.date(2020, 1, 2), dt.date(2020, 2, 1))).run()
    assert not at.exception
    find(at.slider, "Khoảng thời gian").set_value((dt.date(2026, 10, 4), dt.date(2026, 10, 4))).run()
    assert not at.exception


def test_update_and_inflation_controls():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    find(at.checkbox, "Bao gồm CPI sơ bộ").uncheck().run()
    assert not at.exception
    find(at.radio, "Công thức lợi nhuận thực").set_value("Fisher: (1+r)/(1+i) − 1").run()
    assert not at.exception
    find(at.multiselect, "Các quỹ trong ma trận").set_value([]).run()
    assert not at.exception
    find(at.button, "🔄 Cập nhật Dữ liệu Mới (Scrape & ETL)").click().run()
    assert not at.exception
    assert any("ETL hoàn tất" in item.value for item in at.success)
