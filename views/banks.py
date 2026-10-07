import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.transformer import bank_growth, normalize_nav
from views.common import bank_stats, chart, change


def render(nav, summary, rates, capital):
    st.subheader("CCQ và tiết kiệm ngân hàng")
    st.caption("Nguồn: CSV lãi suất ngân hàng đã scrape.")
    if rates.empty:
        st.info("Không có mức lãi suất cho các ngân hàng và kỳ hạn đã chọn.")
        return
    mean, best = bank_stats(rates)
    a, b, c = st.columns(3)
    a.metric("Lãi suất cao nhất", f"{best:.2f}%/năm")
    b.metric("Lãi suất trung bình", f"{mean:.2f}%/năm")
    c.metric("Ngân hàng", str(rates.bank_name.nunique()))
    fig = go.Figure()
    for symbol, group in normalize_nav(nav).groupby("symbol"):
        fig.add_scatter(x=group.date, y=capital * group.normalized_nav / 100, name=symbol, mode="lines")
    dates = pd.date_range(nav.date.min(), nav.date.max(), freq="D")
    years = (dates - dates[0]).days / 365.25
    for name, rate in [("NH trung bình nhóm chọn", mean), ("NH cao nhất nhóm chọn", best)]:
        fig.add_scatter(x=dates, y=bank_growth(capital, rate, years), name=f"{name} ({rate:.2f}%)", line=dict(dash="dash"))
    fig.update_layout(title="Giá trị đầu tư theo NAV và kịch bản lãi suất cố định", yaxis_title="VNĐ", xaxis_title="Ngày")
    chart(fig)
    with st.expander("Cách tính mô phỏng"):
        st.caption("Lãi suất từ lần scrape được giữ cố định, lãi kép hàng năm; không phải lịch sử lãi suất. Trung bình lấy mức tốt nhất mỗi ngân hàng. Chưa tính thuế, phí và rút trước hạn.")
    ordered = rates.sort_values("annual_rate")
    chart(px.bar(ordered, x="annual_rate", y="bank_name", color="deposit_type", orientation="h", barmode="group",
                 title=f"Lãi suất kỳ hạn {int(rates.term_months.iloc[0])} tháng",
                 labels={"annual_rate": "%/năm", "bank_name": "Ngân hàng", "deposit_type": "Hình thức"},
                 height=max(400, rates.bank_name.nunique() * 25)))
    st.subheader("Bộ tính kịch bản đầu tư")
    a, b, c = st.columns(3)
    bank_name = a.selectbox("Ngân hàng tính toán", sorted(rates.bank_name.unique()))
    symbol = b.selectbox("Quỹ tính toán", sorted(summary.symbol))
    years = c.number_input("Số năm mô phỏng", min_value=1, max_value=30, value=5)
    capital_calc = st.number_input("Vốn mô phỏng (VNĐ)", min_value=100_000.0, value=float(capital), step=1_000_000.0)
    bank_rows = rates[rates.bank_name == bank_name]
    channel = st.selectbox("Hình thức gửi", sorted(bank_rows.deposit_type.unique()))
    rate = bank_rows.loc[bank_rows.deposit_type == channel, "annual_rate"].iloc[0]
    cagr = summary.loc[summary.symbol == symbol, "cagr"].iloc[0]
    if not np.isfinite(cagr):
        st.info("Quỹ cần ít nhất hai ngày quan sát để tính CAGR.")
        return
    bank_value = bank_growth(capital_calc, rate, years)
    fund_value = bank_growth(capital_calc, cagr, years)
    comparison = pd.DataFrame({"Kênh": [f"{bank_name} · {channel}", symbol],
                               "Tỷ lệ dùng mô phỏng (%/năm)": [rate, cagr],
                               "Giá trị cuối kỳ (VNĐ)": [bank_value, fund_value],
                               "Lãi/lỗ (VNĐ)": [bank_value - capital_calc, fund_value - capital_calc],
                               "Lợi nhuận (%)": [(bank_value / capital_calc - 1) * 100, (fund_value / capital_calc - 1) * 100]})
    st.dataframe(comparison, hide_index=True, use_container_width=True)
    st.metric("CCQ − ngân hàng", f"{fund_value - bank_value:+,.0f} VNĐ", change((fund_value / bank_value - 1) * 100))
    st.caption("Giả định CAGR lặp lại; kết quả là mô phỏng.")
