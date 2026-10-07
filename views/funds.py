import plotly.express as px
import streamlit as st

from views.common import chart


def render(info, holdings, summary, end):
    st.subheader("Cơ cấu tài sản và so sánh quỹ")
    symbol = st.selectbox("Quỹ cần xem", sorted(summary.symbol))
    fund = info[info.symbol == symbol].iloc[0]
    portfolio = holdings[(holdings.symbol == symbol) & (holdings.update_date <= end)]
    left, right = st.columns([1.3, 1])
    with left:
        if portfolio.empty:
            st.info("Không có snapshot cơ cấu tài sản tại hoặc trước ngày kết thúc đã chọn.")
        else:
            portfolio = portfolio[portfolio.update_date == portfolio.update_date.max()]
            chart(px.pie(portfolio, values="asset_percent", names="asset_type", hole=.6,
                         title=f"{symbol} · cơ cấu tại {portfolio.update_date.max():%d/%m/%Y}"))
            with st.expander("Tỷ trọng chi tiết"):
                st.dataframe(portfolio[["asset_type", "asset_percent"]], hide_index=True)
    with right:
        st.write(f"**{fund.fund_name}**")
        st.write(f"Loại quỹ: {fund.fund_type}")
        st.write(f"Mức độ rủi ro (nguồn): {fund.risk_level}")
        st.metric("Phí quản lý (%/năm)", f"{fund.management_fee:.2f}")
        st.metric("Giá trị mua tối thiểu (VNĐ)", f"{fund.buy_min_value:,.0f}")
        st.caption("Thông tin tại lần cập nhật nguồn.")
    selected = st.multiselect("Các quỹ trong ma trận", sorted(summary.symbol), default=sorted(summary.symbol))
    subset = summary[summary.symbol.isin(selected)]
    if subset.empty:
        st.info("Chọn ít nhất một quỹ để so sánh.")
        return
    metrics = [f"return_{m}m_nav" for m in (1, 3, 6, 12)]
    long = subset.melt(id_vars="symbol", value_vars=metrics, var_name="Kỳ", value_name="Lợi nhuận (%)").dropna()
    long["Kỳ"] = long["Kỳ"].str.replace("return_", "").str.replace("_nav", "").str.upper()
    chart(px.bar(long, x="symbol", y="Lợi nhuận (%)", color="Kỳ", barmode="group", title="Lợi nhuận NAV theo kỳ hạn"))
    st.caption("Tính đến ngày NAV cuối trong kỳ chọn.")
    scatter = subset.merge(info[["symbol", "management_fee", "risk_level", "fund_type"]], on="symbol").dropna(subset=["return_12m_nav", "management_fee"])
    if not scatter.empty:
        fig = px.scatter(scatter, x="management_fee", y="return_12m_nav", color="fund_type", text="symbol",
                         hover_data=["risk_level", "max_drawdown"], title="Phí quản lý và lợi nhuận NAV 12 tháng",
                         labels={"management_fee": "Phí quản lý (%/năm)", "return_12m_nav": "Lợi nhuận 12M (%)"})
        fig.add_vline(x=scatter.management_fee.median(), line_dash="dot")
        fig.add_hline(y=scatter.return_12m_nav.median(), line_dash="dot")
        fig.update_traces(textposition="top center", marker_size=16)
        chart(fig)
        st.caption("Đường nét đứt: trung vị. Phí quản lý không đại diện mức rủi ro.")
