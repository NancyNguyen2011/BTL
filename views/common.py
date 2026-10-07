"""Hàm biểu đồ và chọn snapshot dùng chung các tab."""
import pandas as pd
import streamlit as st


def chart(figure):
    figure.update_layout(template="plotly_white", font=dict(family="Arial", size=13),
                         margin=dict(l=15, r=15, t=55, b=25), legend_title_text="")
    st.plotly_chart(figure, use_container_width=True)


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
