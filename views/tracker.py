"""Banner 3 nguồn phản ánh phạm vi quan sát thật và lịch sử ETL."""
import streamlit as st


def render(data):
    nav, bank, cpi = data["fund_nav"], data["bank_rates"], data["macro_cpi"]
    a, b, c = st.columns(3)
    with a:
        st.info(f"**Fmarket · {nav.symbol.nunique()} quỹ**\n\n"
                f"NAV: {nav.date.min():%d/%m/%Y} → {nav.date.max():%d/%m/%Y}")
    with b:
        st.info(f"**Ngân hàng · {bank.bank_name.nunique()} đơn vị**\n\n"
                f"Quét nguồn: {bank.scrape_date.max():%d/%m/%Y %H:%M}")
    with c:
        st.info(f"**CPI · {len(cpi)} tháng**\n\n"
                f"{cpi.date.min():%m/%Y} → {cpi.date.max():%m/%Y} · {cpi.iloc[-1]['status']}")
    with st.expander("🔍 Chi tiết Trạng thái Dữ liệu & Lịch sử Cập nhật"):
        st.write(f"NAV có {nav.date.nunique():,} ngày quan sát, {len(nav):,} bản ghi. Mã quỹ: "
                 + ", ".join(sorted(nav.symbol.unique())))
        rates = bank[(bank.term_months == 12) & bank.annual_rate.notna()]
        if not rates.empty:
            best = rates.loc[rates.annual_rate.idxmax()]
            st.write(f"Lãi suất 12 tháng cao nhất theo nhãn nguồn: {best.bank_name}, {best.deposit_type}, {best.annual_rate:.2f}%/năm.")
        st.dataframe(cpi.groupby("status").size().rename("Số tháng"), use_container_width=True)
        st.caption("Thời điểm chạy ETL khác thời điểm cập nhật nguồn. File hiện có không cung cấp URL xuất xứ để xác minh trực tiếp.")
        st.dataframe(data["update_history"], hide_index=True, use_container_width=True)
        st.write("**Báo cáo chất lượng dữ liệu**")
        st.dataframe(data["quality_report"], hide_index=True, use_container_width=True)
        if not data["rejected_rows"].empty:
            st.write("**Dòng được cách ly (không dùng tính lợi nhuận)**")
            st.dataframe(data["rejected_rows"], hide_index=True, use_container_width=True)
        st.download_button("Tải báo cáo chất lượng CSV", data["quality_report"].to_csv(index=False).encode("utf-8-sig"),
                           "quality_report.csv", "text/csv")
