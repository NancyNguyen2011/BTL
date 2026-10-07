"""Hàm biểu đồ và chọn snapshot dùng chung các tab."""
import pandas as pd
import streamlit as st


def chart(figure):
    figure.update_layout(template="plotly_white", font=dict(family="Arial", size=14, color="#284766"),
                         paper_bgcolor="white", plot_bgcolor="white",
                         margin=dict(l=25, r=25, t=65, b=70), legend_title_text="",
                         legend=dict(orientation="h", y=-.22, x=0),
                         colorway=["#2563eb", "#0d9488", "#7c3aed", "#ea580c", "#0891b2"],
                         hoverlabel=dict(bgcolor="white", font_size=14))
    figure.update_xaxes(showgrid=False, automargin=True)
    figure.update_yaxes(gridcolor="#edf2f9", automargin=True)
    for trace in figure.data:
        if trace.type == "scatter" and trace.mode and "lines" in trace.mode:
            trace.line.width = 2.8
    st.plotly_chart(figure, use_container_width=True, theme=None,
                    config={"displaylogo": False, "scrollZoom": False})


def change(value, suffix="%"):
    """Dấu +/- để st.metric tự hiển thị mũi tên và màu xanh/đỏ đúng chiều."""
    return None if pd.isna(value) else f"{value:+.2f}{suffix}"


def percent(value):
    return "Chưa đủ dữ liệu" if pd.isna(value) else f"{value:,.2f}%"


def latest_rates(bank, term, names):
    """Snapshot gần nhất của mỗi ngân hàng/hình thức; không lấp NULL bằng giá cũ."""
    selected = bank[(bank.term_months == term) & bank.bank_name.isin(names)]
    return (selected.sort_values("scrape_date").drop_duplicates(["bank_name", "deposit_type"], keep="last")
            .dropna(subset=["annual_rate"]))


def bank_stats(rates):
    # Mỗi ngân hàng đóng góp một mức tốt nhất, tránh ngân hàng có 2 kênh bị đếm đôi.
    best = rates.groupby("bank_name").annual_rate.max()
    return best.mean(), best.max()
