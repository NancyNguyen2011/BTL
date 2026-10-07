"""Ghi cả bộ bảng bằng một transaction để lỗi không làm hỏng snapshot đang dùng."""
import sqlite3
from contextlib import closing
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import DB_PATH

TABLES = {"fund_info", "fund_nav", "fund_holdings", "bank_rates", "macro_cpi", "quality_report", "rejected_rows"}
DATES = {"date", "month", "update_date", "scrape_date", "web_update_time"}


def _value(value):
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat(sep=" ")
    return value.item() if isinstance(value, np.generic) else value


def save_database(tables, run, path=DB_PATH):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if set(tables) != TABLES:
        raise ValueError("Snapshot phải chứa đủ 7 bảng dữ liệu và kiểm toán")
    # Không dùng pandas.to_sql vì sqlite3 có thể commit sớm từng bảng.
    with closing(sqlite3.connect(path, timeout=30)) as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        for name, frame in tables.items():
            definitions = []
            for column, dtype in frame.dtypes.items():
                kind = "INTEGER" if pd.api.types.is_integer_dtype(dtype) or pd.api.types.is_bool_dtype(dtype) else (
                    "REAL" if pd.api.types.is_numeric_dtype(dtype) else "TEXT")
                definitions.append(f'"{column}" {kind}')
            conn.execute(f'DROP TABLE IF EXISTS "{name}"')
            conn.execute(f'CREATE TABLE "{name}" ({", ".join(definitions)})')
            placeholders = ",".join("?" for _ in frame.columns)
            conn.executemany(f'INSERT INTO "{name}" VALUES ({placeholders})',
                             [tuple(_value(v) for v in row) for row in frame.itertuples(index=False, name=None)])
        conn.execute("CREATE UNIQUE INDEX nav_key ON fund_nav(fund_id, date)")
        conn.execute("CREATE UNIQUE INDEX fund_key ON fund_info(fund_id)")
        conn.execute("CREATE UNIQUE INDEX cpi_key ON macro_cpi(date)")
        conn.execute("CREATE TABLE IF NOT EXISTS update_history (id INTEGER PRIMARY KEY, updated_at TEXT, mode TEXT, source_hashes TEXT, row_counts TEXT)")
        conn.execute("INSERT INTO update_history(updated_at,mode,source_hashes,row_counts) VALUES (?,?,?,?)",
                     (run["updated_at"], run["mode"], run["source_hashes"], run["row_counts"]))


def load_database(path=DB_PATH):
    with closing(sqlite3.connect(f"{Path(path).resolve().as_uri()}?mode=ro", uri=True)) as conn:
        result = {name: pd.read_sql_query(f'SELECT * FROM "{name}"', conn) for name in TABLES}
        result["update_history"] = pd.read_sql_query("SELECT * FROM update_history ORDER BY id DESC LIMIT 50", conn)
    for frame in result.values():
        for c in set(frame) & DATES:
            frame[c] = pd.to_datetime(frame[c])
    return result
