import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.transformer import bank_growth, normalize_nav
from views.common import bank_stats, chart


def render(nav, summary, rates, capital):
    st.subheader("CCQ và tiết kiệm ngân hàng")
    st.warning("Lãi suất ngân hàng là snapshot, chưa có lịch sử và điều kiện áp dụng. Kỳ hạn giữ theo nhãn CSV nguồn có dấu hiệu lệch tiêu đề; cần xác minh trước khi sử dụng ngoài bài thực hành.")
    if rates.empty:
        st.info("Không có mức lãi suất cho các ngân hàng và kỳ hạn đã chọn.")
        return
    mean, best = bank_stats(rates)
    fig = go.Figure()
    for symbol, group in normalize_nav(nav).groupby("symbol"):
        fig.add_scatter(x=group.date, y=capital * group.normalized_nav / 100, name=symbol, mode="lines")
    dates = pd.date_range(nav.date.min(), nav.date.max(), freq="D")
    years = (dates - dates[0]).days / 365.25
    for name, rate in [("NH trung bình nhóm chọn", mean), ("NH cao nhất nhóm chọn", best)]:
        fig.add_scatter(x=dates, y=bank_growth(capital, rate, years), name=f"{name} ({rate:.2f}%)", line=dict(dash="dash"))
    fig.update_layout(title="Giá trị đầu tư theo NAV và kịch bản lãi suất cố định", yaxis_title="VNĐ", xaxis_title="Ngày")
    chart(fig)
    st.caption("Ngân hàng: lãi kép hàng năm, lãi suất snapshot giữ cố định, kể cả khi kéo lùi về quá khứ. Trung bình lấy mức tốt nhất của mỗi ngân hàng trong nhóm chọn. Chưa tính thuế/phí giao dịch hoặc rút trước hạn. Mỗi quỹ nhận vốn tại ngày gốc riêng trong bảng tổng quan.")
    ordered = rates.sort_values("annual_rate")
    chart(px.bar(ordered, x="annual_rate", y="bank_name", color="deposit_type", orientation="h", barmode="group",
                 title=f"Lãi suất kỳ hạn {int(rates.term_months.iloc[0])} tháng · theo nhãn nguồn",
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
    st.metric("Chênh lệch CCQ − ngân hàng", f"{fund_value - bank_value:,.0f} VNĐ", f"{(fund_value / bank_value - 1) * 100:.2f}% so với giá trị ngân hàng")
    st.caption("Mô phỏng quỹ giả định CAGR của cửa sổ đã chọn lặp lại trong tương lai; đây không phải dự báo hay cam kết lợi nhuận.")
