import plotly.express as px
import pandas as pd
import streamlit as st

from src.transformer import normalize_nav
from views.common import chart, percent, change


def render(nav, summary, rates, cpi):
    st.subheader("Hiệu quả trong giai đoạn đã chọn")
    a, b, c, d = st.columns(4)
    top = summary.loc[summary.total_return.idxmax()]
    a.metric(f"Dẫn đầu · {top.symbol}", percent(top.total_return), change(top.total_return), help="Lợi nhuận trong giai đoạn chọn")
    d.metric("CAGR · " + top.symbol, percent(top.cagr), change(top.cagr), help="Tăng trưởng quy đổi năm")
    if not rates.empty:
        bank = rates.loc[rates.annual_rate.idxmax()]
        b.metric(f"Ngân hàng · {bank.bank_name} · {int(bank.term_months)}M", percent(bank.annual_rate))
    else:
        b.metric("Lãi suất ngân hàng", "Không có dữ liệu")
    if not cpi.empty:
        delta = cpi.iloc[-1].cpi_yoy - cpi.iloc[-2].cpi_yoy if len(cpi) > 1 else float("nan")
        c.metric(f"CPI YoY · {cpi.iloc[-1].date:%m/%Y}", percent(cpi.iloc[-1].cpi_yoy), change(delta, " điểm %"), delta_color="inverse", help="Chênh lệch CPI YoY so với tháng trước")
    else:
        c.metric("CPI YoY", "Không có dữ liệu")
    normalized = normalize_nav(nav)
    chart(px.line(normalized, x="date", y="normalized_nav", color="symbol",
                  title="Tăng trưởng NAV · Base 100", labels={"date": "Ngày", "normalized_nav": "Điểm (gốc 100)"}))
    st.caption("Gốc 100 tại ngày quan sát đầu của mỗi quỹ trong kỳ chọn.")
    choice = st.radio("Xếp hạng theo", ["Giai đoạn đã chọn", "12 tháng gần nhất"], horizontal=True)
    metric = "total_return" if choice == "Giai đoạn đã chọn" else "return_12m_nav"
    ranking = summary.dropna(subset=[metric]).sort_values(metric)
    if ranking.empty:
        st.info("Chưa đủ lịch sử cho lợi nhuận 12 tháng.")
    else:
        chart(px.bar(ranking, x=metric, y="symbol", orientation="h", color="symbol",
                     labels={metric: "Lợi nhuận (%)", "symbol": "Quỹ"}, title="Xếp hạng hiệu suất quan sát"))
    left, right = st.columns(2)
    with left:
        scatter = summary.dropna(subset=["cagr", "max_drawdown"])
        if not scatter.empty:
            fig = px.scatter(scatter, x="max_drawdown", y="cagr", color="symbol", text="symbol",
                             title="Tăng trưởng & sụt giảm", labels={"max_drawdown": "Sụt giảm tối đa (%)", "cagr": "CAGR (%/năm)"})
            fig.update_traces(marker_size=14, textposition="top center")
            chart(fig)
    with right:
        # Bỏ hai tháng biên chưa đầy đủ; không bù giá cho tháng thiếu.
        prices = nav.pivot(index="date", columns="symbol", values="nav").resample("ME").last()
        returns = prices.pct_change(fill_method=None).iloc[1:] * 100
        if not returns.empty and nav.date.max().normalize() < nav.date.max().normalize() + pd.offsets.MonthEnd(0):
            returns = returns.iloc[:-1]
        long = returns.melt(var_name="Quỹ", value_name="Lợi nhuận tháng (%)").dropna()
        if not long.empty:
            chart(px.box(long, x="Quỹ", y="Lợi nhuận tháng (%)", color="Quỹ", points="outliers", title="Phân phối lợi nhuận tháng"))
        else:
            st.info("Chọn khoảng dài hơn để xem biểu đồ hộp.")
    with st.expander("Số liệu chi tiết"):
        st.dataframe(summary, hide_index=True, use_container_width=True)
        st.download_button("Tải CSV", summary.to_csv(index=False).encode("utf-8-sig"), "fund_comparison.csv", "text/csv")
