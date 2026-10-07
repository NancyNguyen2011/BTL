import plotly.express as px
import streamlit as st

from src.transformer import normalize_nav
from views.common import chart, percent


def render(nav, summary, rates, cpi):
    st.subheader("Hiệu quả trong giai đoạn đã chọn")
    a, b, c = st.columns(3)
    top = summary.loc[summary.total_return.idxmax()]
    a.metric(f"Quỹ dẫn đầu · {top.symbol}", percent(top.total_return))
    if not rates.empty:
        bank = rates.loc[rates.annual_rate.idxmax()]
        b.metric(f"Ngân hàng · {bank.bank_name} · {int(bank.term_months)}M", percent(bank.annual_rate))
    else:
        b.metric("Lãi suất ngân hàng", "Không có dữ liệu")
    if not cpi.empty:
        c.metric(f"CPI YoY · {cpi.iloc[-1].date:%m/%Y}", percent(cpi.iloc[-1].cpi_yoy))
    else:
        c.metric("CPI YoY", "Không có dữ liệu")
    normalized = normalize_nav(nav)
    chart(px.line(normalized, x="date", y="normalized_nav", color="symbol",
                  title="Tăng trưởng NAV · Base 100", labels={"date": "Ngày", "normalized_nav": "Điểm (gốc 100)"}))
    st.caption("Mỗi quỹ bắt đầu ở lần quan sát đầu tiên trong khoảng chọn. Ngày gốc có thể khác nhau; xem bảng bên dưới.")
    choice = st.radio("Xếp hạng theo", ["Giai đoạn đã chọn", "12 tháng gần nhất"], horizontal=True)
    metric = "total_return" if choice == "Giai đoạn đã chọn" else "return_12m_nav"
    ranking = summary.dropna(subset=[metric]).sort_values(metric)
    if ranking.empty:
        st.info("Chưa đủ lịch sử cho lợi nhuận 12 tháng.")
    else:
        chart(px.bar(ranking, x=metric, y="symbol", orientation="h", color="symbol",
                     labels={metric: "Lợi nhuận (%)", "symbol": "Quỹ"}, title="Xếp hạng hiệu suất quan sát"))
    st.dataframe(summary, hide_index=True, use_container_width=True)
    st.download_button("Tải kết quả so sánh CSV", summary.to_csv(index=False).encode("utf-8-sig"), "fund_comparison.csv", "text/csv")
