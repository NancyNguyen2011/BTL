"""Điều phối thu thập → làm sạch → tính chỉ số → lưu SQLite; dùng chung CLI/UI."""
import argparse
import hashlib
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.cleaner import clean_data, read_raw
from src.config import DB_PATH, FILES, RAW_DIR
from src.database import save_database
from src.scraper import collect_data
from src.transformer import transform_data


def run_pipeline(raw_dir=RAW_DIR, db_path=DB_PATH, sources_config=None):
    # Giữ dữ liệu đầu vào tải về trong staging: tải/schema lỗi thì DB cũ nguyên vẹn.
    with tempfile.TemporaryDirectory(prefix="investment_etl_") as temporary:
        mode = collect_data(temporary, raw_dir, sources_config)
        tables = transform_data(clean_data(read_raw(temporary)))
        hashes = {name: hashlib.sha256((Path(temporary) / file).read_bytes()).hexdigest()
                  for name, file in FILES.items()}
        run = {"updated_at": datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds"),
               "mode": mode, "source_hashes": json.dumps(hashes),
               "row_counts": json.dumps({k: len(v) for k, v in tables.items()})}
        save_database(tables, run, db_path)
    return run


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy ETL phân tích đầu tư")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--db-path", type=Path, default=DB_PATH)
    parser.add_argument("--sources-config", type=Path)
    args = parser.parse_args()
    print(json.dumps(run_pipeline(args.raw_dir, args.db_path, args.sources_config), ensure_ascii=False, indent=2))
