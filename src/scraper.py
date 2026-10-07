"""Stage 1–2: tiếp nhận 5 CSV từ file hoặc endpoint CSV HTTPS được cấu hình.

Không đoán API Fmarket hay gắn nhãn 'dữ liệu mới' cho file cũ. Mặc định
đọc data/raw; khi có cấu hình, tải vào staging rồi kiểm tra toàn bộ trước ETL.
"""
import json
import shutil
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from src.config import FILES, RAW_DIR


def collect_data(destination, raw_dir=RAW_DIR, sources_config=None):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    urls = {}
    if sources_config:
        urls = json.loads(Path(sources_config).read_text(encoding="utf-8")).get("csv_urls", {})
        if set(urls) - set(FILES):
            raise ValueError("Cấu hình chứa tên bảng không hợp lệ")
    for name, filename in FILES.items():
        url = urls.get(name)
        target = destination / filename
        if url:
            if urlparse(url).scheme != "https":
                raise ValueError("Endpoint dữ liệu phải dùng HTTPS")
            request = Request(url, headers={"User-Agent": "InvestmentAnalytics/1.0", "Accept": "text/csv"})
            with urlopen(request, timeout=30) as response:
                payload = response.read(30_000_001)
            if len(payload) > 30_000_000:
                raise ValueError(f"{name}: file vượt giới hạn 30 MB")
            target.write_bytes(payload)
        else:
            source = Path(raw_dir) / filename
            if not source.is_file():
                raise ValueError(f"Thiếu file {source}")
            shutil.copy2(source, target)
    return "HTTPS CSV + file" if any(urls.values()) else "File CSV cục bộ"
