"""Giao diện xanh–trắng, ưu tiên số liệu và không dùng icon trang trí."""
import streamlit as st


def apply_style():
    st.markdown("""<style>
    .stApp {background:#f0f6ff;color:#142e50;}
    [data-testid="stHeader"] {background:rgba(240,246,255,.95);}
    [data-testid="stSidebar"] {background:#fff;border-right:1px solid #dbe7f7;}
    .block-container {padding-top:2rem;max-width:1500px;}
    h1 {font-size:2rem!important;letter-spacing:-.7px;color:#123e73;}
    h2,h3 {color:#174675;}
    [data-testid="stMetric"] {background:white;border:1px solid #dce8f8;
      border-radius:18px;padding:20px;box-shadow:0 5px 18px #173f7308;}
    [data-testid="stMetricValue"] {font-size:2.1rem;font-weight:750;}
    [data-testid="stMetricLabel"] {color:#526987;font-size:.9rem;}
    [data-testid="stPlotlyChart"], [data-testid="stExpander"],
    [data-testid="stAlert"], [data-testid="stDataFrame"] {
      border-radius:16px;overflow:hidden;border:1px solid #dce8f8;background:#fff;}
    .stButton button,.stDownloadButton button {border-radius:12px;border-color:#c7dbf5;}
    [data-baseweb="select"] > div,[data-baseweb="input"] {border-radius:10px!important;}
    [data-testid="stSidebar"] [role="radiogroup"] {gap:6px;}
    [data-testid="stSidebar"] [role="radiogroup"] label {
      padding:10px 14px;border-radius:12px;background:#f3f7fd;}
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
      background:#deedff;color:#145bb3;font-weight:700;}
    .source-card {border:1px solid #dce8f8;border-radius:14px;background:#fff;
      padding:14px 18px;margin-bottom:12px;}
    .source-card strong {font-size:15px;color:#174675;}
    .source-card p {font-size:12px;color:#647894;margin:5px 0 0;}
    </style>""", unsafe_allow_html=True)
