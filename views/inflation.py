import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from views.common import bank_stats, chart


def render(nav, cpi, rates):
    st.subheader("Lợi nhuận thực và sức mua")
    if cpi.empty:
        st.info("Không có CPI cho khoảng thời gian đã chọn.")
        return
    include_preliminary = st.checkbox("Bao gồm CPI sơ bộ", value=True)
    if not include_preliminary:
        cpi = cpi[cpi.status == "Chính thức"]
    if cpi.empty:
        st.info("Không còn CPI chính thức trong khoảng chọn.")
        return
    monthly = nav.sort_values("date").groupby(["symbol", "month"], as_index=False).tail(1)
    monthly = monthly[monthly.month.isin(cpi.date)]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=cpi.date, y=cpi.cpi_yoy, name="CPI YoY", opacity=.4,
                         customdata=cpi.status, hovertemplate="%{x|%m/%Y}: %{y:.2f}% · %{customdata}<extra></extra>"), secondary_y=False)
    for symbol, group in monthly.groupby("symbol"):
        fig.add_trace(go.Scatter(x=group.month, y=group.return_12m_nav, name=f"{symbol} · 12M"), secondary_y=True)
    if not rates.empty:
        mean, _ = bank_stats(rates)
        fig.add_trace(go.Scatter(x=cpi.date, y=[mean] * len(cpi), name="NH snapshot cố định", line=dict(dash="dash")), secondary_y=True)
    fig.update_layout(title="CPI YoY và lợi nhuận NAV trailing 12 tháng")
    fig.update_yaxes(title_text="CPI YoY (%)", secondary_y=False)
    fig.update_yaxes(title_text="NAV 12M / lãi suất NH (%/năm)", secondary_y=True)
    chart(fig)
    st.caption("Đối chiếu hồi cứu cùng tháng, không giả định CPI đã công bố vào ngày giao dịch. Đường NH là kịch bản snapshot, không phải chuỗi lãi suất lịch sử.")
    available = monthly.dropna(subset=["return_12m_nav", "cpi_yoy"])
    if available.empty:
        st.info("Chưa đủ NAV 12 tháng và CPI cùng kỳ để tính lợi nhuận thực.")
        return
    months = sorted(available.month.unique())
    month = st.selectbox("Tháng đối chiếu lợi nhuận thực", months, index=len(months) - 1,
                         format_func=lambda x: pd.Timestamp(x).strftime("%m/%Y"))
    compared = available[available.month == month][["symbol", "return_12m_nav", "cpi_yoy"]].rename(columns={"symbol": "Kênh", "return_12m_nav": "Danh nghĩa (%)"})
    inflation = float(cpi.loc[cpi.date == month, "cpi_yoy"].iloc[0])
    if not rates.empty:
        mean, best = bank_stats(rates)
        compared = pd.concat([compared, pd.DataFrame({"Kênh": ["NH trung bình (kịch bản)", "NH cao nhất (kịch bản)"], "Danh nghĩa (%)": [mean, best], "cpi_yoy": [inflation, inflation]})], ignore_index=True)
    exact = st.radio("Công thức lợi nhuận thực", ["Xấp xỉ: danh nghĩa − CPI", "Fisher: (1+r)/(1+i) − 1"], horizontal=True)
    compared["Thực (%)"] = (compared["Danh nghĩa (%)"] - compared.cpi_yoy if exact.startswith("Xấp")
                             else ((1 + compared["Danh nghĩa (%)"] / 100) / (1 + compared.cpi_yoy / 100) - 1) * 100)
    compared["Sức mua"] = compared["Thực (%)"].map(lambda x: "Tăng" if x >= 0 else "Giảm")
    fig = px.bar(compared.sort_values("Thực (%)"), x="Thực (%)", y="Kênh", orientation="h", color="Sức mua",
                 color_discrete_map={"Tăng": "#15803d", "Giảm": "#dc2626"}, title="Lợi nhuận thực 12 tháng · cùng kỳ CPI")
    fig.add_vline(x=0, line_color="#334155")
    chart(fig)
    st.dataframe(compared, hide_index=True, use_container_width=True)
    winners = compared.loc[compared["Thực (%)"] > 0, "Kênh"].tolist()
    st.write("Kênh có lợi nhuận thực dương trong kỳ: " + (", ".join(winners) if winners else "Không có trong nhóm chọn"))
    st.caption("CPI MoM có tháng thiếu nên không suy diễn sức mua tích lũy toàn kỳ bằng cách cộng CPI YoY.")
