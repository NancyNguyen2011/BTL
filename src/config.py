"""Đường dẫn cố định theo project root, không phụ thuộc thư mục chạy lệnh."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "processed" / "invest_analytics.db"
FILES = {
    "fund_info": "raw_fund_info.csv",
    "fund_nav": "raw_fund_nav_daily.csv",
    "fund_holdings": "raw_fund_holdings_asset.csv",
    "bank_rates": "raw_bank_interest_rates.csv",
    "macro_cpi": "raw_macro_cpi.csv",
}
