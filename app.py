"""Stage 5: entry point Streamlit, điều phối bộ lọc và 4 tab."""
import os

import pandas as pd
import streamlit as st

from src.config import DB_PATH
from src.database import load_database
from src.pipeline import run_pipeline
from src.transformer import period_summary
from views import banks, funds, inflation, overview, tracker
from views.common import latest_rates
from views.style import apply_style

st.set_page_config(page_title="NTTT · Phân tích đầu tư", layout="wide")


@st.cache_data(show_spinner=False)
def load_snapshot(version):
    """Mtime thay đổi sau transaction sẽ vô hiệu cache của phiên khác."""
    return load_database()


def main():
    apply_style()
    st.title("Hiệu quả đầu tư")
    st.caption("Chứng chỉ quỹ · Ngân hàng · CPI  |  NTTT~B23DCKD069")
    with st.sidebar:
        st.header("NTTT Analytics")
        page = st.radio("Danh mục", ["Tổng quan", "Cơ cấu quỹ", "Ngân hàng", "Lạm phát & sức mua"], key="navigation")
        refresh = st.button("Cập nhật dữ liệu", use_container_width=True, type="primary")
        st.divider()
        st.subheader("Bộ lọc")
    if refresh or not DB_PATH.exists():
        try:
            with st.spinner("Thu thập → làm sạch → tạo chỉ số → lưu SQLite..."):
                result = run_pipeline(sources_config=os.getenv("INVEST_SOURCES_CONFIG"))
            load_snapshot.clear()
            st.session_state["update_message"] = f"ETL hoàn tất · {result['mode']} · {result['updated_at']}"
            st.rerun()
        except Exception as exc:
            st.error(f"Cập nhật thất bại: {exc}. Snapshot đã lưu trước đó được giữ nguyên.")
            if not DB_PATH.exists():
                st.stop()
    if "update_message" in st.session_state:
        st.success(st.session_state.pop("update_message"))
    try:
        data = load_snapshot(DB_PATH.stat().st_mtime_ns)
    except Exception as exc:
        st.error(f"Không đọc được CSDL: {exc}. Hãy chạy lại cập nhật dữ liệu.")
        st.stop()
    tracker.render(data)
    nav = data["fund_nav"]
    with st.sidebar:
        low, high = nav.date.min().date(), nav.date.max().date()
        if low == high:
            start, end = low, high
            st.caption(f"Chỉ có dữ liệu ngày {low:%d/%m/%Y}")
        else:
            start, end = st.slider("Khoảng thời gian", min_value=low, max_value=high, value=(low, high), format="DD/MM/YYYY")
        kind = st.selectbox("Loại quỹ", ["Tất cả"] + sorted(data["fund_info"].fund_type.unique()))
        capital = st.number_input("Vốn đầu tư ban đầu (VNĐ)", min_value=100_000.0, value=100_000_000.0, step=1_000_000.0)
        term = st.selectbox("Kỳ hạn ngân hàng (tháng)", [6, 12, 24], index=1)
        names = sorted(data["bank_rates"].bank_name.unique())
        all_banks = st.checkbox("Tất cả ngân hàng", value=True)
        selected_banks = names if all_banks else st.multiselect("Ngân hàng so sánh", names, default=[])
    filtered = nav[nav.date.between(pd.Timestamp(start), pd.Timestamp(end))]
    if kind != "Tất cả":
        filtered = filtered[filtered.fund_type == kind]
    if filtered.empty:
        st.info("Không có NAV cho khoảng thời gian và loại quỹ đã chọn.")
        return
    summary = period_summary(filtered)
    rates = latest_rates(data["bank_rates"], term, selected_banks)
    cpi = data["macro_cpi"]
    cpi = cpi[cpi.date.between(pd.Timestamp(start).to_period("M").to_timestamp(), pd.Timestamp(end))]
    if page == "Tổng quan":
        overview.render(filtered, summary, rates, cpi)
    elif page == "Cơ cấu quỹ":
        funds.render(data["fund_info"], data["fund_holdings"], summary, pd.Timestamp(end))
    elif page == "Ngân hàng":
        banks.render(filtered, summary, rates, capital)
    else:
        inflation.render(filtered, cpi, rates)


if __name__ == "__main__":
    main()
