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

st.set_page_config(page_title="NTTT · Phân tích đầu tư", page_icon="📊", layout="wide")


@st.cache_data(show_spinner=False)
def load_snapshot(version):
    """Mtime thay đổi sau transaction sẽ vô hiệu cache của phiên khác."""
    return load_database()


def main():
    st.title("📊 BÁO CÁO PHÂN TÍCH VÀ SO SÁNH HIỆU QUẢ ĐẦU TƯ")
    st.markdown("**CHỨNG CHỈ QUỸ (FMARKET) VS LÃI SUẤT NGÂN HÀNG VS CHỈ SỐ LẠM PHÁT (CPI)**")
    st.caption("🎓 Sinh viên thực hiện: NTTT~B23DCKD069")
    with st.sidebar:
        st.header("Điều khiển phân tích")
        st.caption("Nguồn cập nhật: HTTPS CSV đã cấu hình" if os.getenv("INVEST_SOURCES_CONFIG") else "Nguồn cập nhật: data/raw/ (file cục bộ)")
        refresh = st.button("🔄 Cập nhật Dữ liệu Mới (Scrape & ETL)", use_container_width=True)
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
        selected_banks = st.multiselect("Ngân hàng so sánh", names, default=names)
        st.caption("Lãi suất dùng snapshot mới nhất của nguồn; không bị diễn giải là lịch sử theo thanh thời gian.")
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
    tabs = st.tabs(["📈 Tổng quan", "🍩 Cơ cấu CCQ", "🏦 CCQ vs Ngân hàng", "📉 Lợi nhuận thực & CPI"])
    with tabs[0]:
        overview.render(filtered, summary, rates, cpi)
    with tabs[1]:
        funds.render(data["fund_info"], data["fund_holdings"], summary, pd.Timestamp(end))
    with tabs[2]:
        banks.render(filtered, summary, rates, capital)
    with tabs[3]:
        inflation.render(filtered, cpi, rates)


if __name__ == "__main__":
    main()
