# Phân tích CCQ, lãi suất ngân hàng và CPI

**Sinh viên: NTTT~B23DCKD069**. Ứng dụng Streamlit bốn tab với pipeline CSV → làm sạch → chỉ số tài chính → SQLite và notebook EDA/Data Mining để thuyết trình.

## Chạy dự án

Yêu cầu Python 3.10 trở lên; đã kiểm tra với Python 3.12. Tại thư mục dự án:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.pipeline
python -m streamlit run app.py
```

Mở địa chỉ mà Streamlit in ra (mặc định `http://localhost:8501`). Nếu chưa có DB, ứng dụng tự tạo từ `data/raw/`. Không cần kết nối mạng để phân tích bộ dữ liệu hiện có sau khi cài thư viện.

```powershell
python -m pytest -q
```

## Kiến trúc hai tầng và các stage

```text
BTL/
├── app.py                         # Stage 5: entry point, sidebar, điều phối 4 tab
├── src/
│   ├── config.py                  # Đường dẫn và danh mục 5 file
│   ├── scraper.py                 # Stage 1–2: CSV từ file/HTTPS vào staging
│   ├── cleaner.py                 # Stage 3: schema, parsing, cách ly lỗi, joins
│   ├── transformer.py             # Stage 4: Base 100, returns, drawdown, CPI
│   ├── database.py                # Stage 4: transaction SQLite, đọc snapshot
│   └── pipeline.py                # Điều phối toàn bộ, dùng chung CLI và UI
├── views/
│   ├── common.py                  # Plotly và chọn snapshot ngân hàng
│   ├── tracker.py                 # Banner 3 nguồn, lịch sử và báo cáo chất lượng
│   ├── overview.py                # Tab 1: KPI, NAV chuẩn hóa, xếp hạng
│   ├── funds.py                   # Tab 2: donut, factsheet, nhóm cột, scatter
│   ├── banks.py                   # Tab 3: mô phỏng, xếp hạng lãi suất, calculator
│   └── inflation.py               # Tab 4: biểu đồ 2 trục, real return phân kỳ
├── notebooks/
│   ├── 01_eda_and_mining.ipynb     # Tầng lab: Markdown, code, biểu đồ, insight
│   └── build_notebook.py           # Tiện ích tái tạo notebook (xóa output cũ)
├── data/
│   ├── raw/                       # 5 CSV đầu vào vận hành
│   └── processed/invest_analytics.db
├── raw_csv/                       # Bản CSV được cung cấp, giữ nguyên
├── docs/
│   ├── streamlit.md               # Đặc tả giao diện gốc
│   └── tổ chức folder.md          # Đặc tả cấu trúc gốc
├── tests/                         # Pipeline, transaction, tương tác Streamlit
├── sources.example.json           # Cấu hình endpoint CSV tùy chọn
└── requirements.txt
```

Tên notebook theo yêu cầu trực tiếp là `01_eda_and_mining.ipynb`; các tên ví dụ khác trong tài liệu folder được hợp nhất vào file này. Dữ liệu ban đầu nằm ở `raw_csv/`, đã sao chép sang `data/raw/` để đúng cấu trúc yêu cầu.

## Sử dụng giao diện

1. Banner đọc trực tiếp phạm vi ngày NAV, số ngân hàng, thời điểm quét, số tháng CPI và trạng thái sơ bộ. Mở expander để xem lịch sử ETL, SHA-256 của file nguồn, số dòng, lỗi và bản ghi cách ly.
2. Sidebar chọn khoảng ngày, loại quỹ, vốn, kỳ hạn 6/12/24 tháng và danh sách ngân hàng. Danh sách quỹ/ngân hàng được nhận diện tự động, không cố định 5 quỹ.
3. Tab tổng quan tính lại Base 100 và lợi nhuận trên cửa sổ đã chọn. Có lựa chọn xếp hạng lợi nhuận giai đoạn hoặc trailing 12 tháng và tải CSV.
4. Tab cơ cấu dùng snapshot tài sản gần nhất tại hoặc trước ngày kết thúc; nếu không có thì hiển thị trạng thái thiếu. Phí, rủi ro và giá trị mua tối thiểu là metadata hiện có, không giả định có lịch sử.
5. Tab ngân hàng mô phỏng vốn theo NAV và hai đường ngân hàng (trung bình/cao nhất), phân màu Online/OTC và tính chênh lệch bằng VNĐ, tỷ lệ %. Calculator cho chọn quỹ, ngân hàng, hình thức, vốn và số năm.
6. Tab CPI có bật/tắt dữ liệu sơ bộ, chọn tháng đối chiếu và công thức xấp xỉ/Fisher. Những quỹ thiếu lịch sử 12 tháng không được gán lợi nhuận bằng 0.

Khoảng ngày tác động NAV, CPI và ngày chọn cơ cấu tài sản. Ngân hàng chỉ có snapshot hiện tại nên luôn được ghi nhãn kịch bản, không dựng lịch sử giả theo thanh thời gian. Bộ lọc loại quỹ chỉ tác động các phân tích quỹ; vốn và lựa chọn ngân hàng tác động các phép so sánh liên quan.

## Cập nhật tự động

Nút **🔄 Cập nhật Dữ liệu Mới (Scrape & ETL)** gọi `src.pipeline.run_pipeline`, thu thập vào thư mục tạm, kiểm tra đủ file/schema, làm sạch, biến đổi, ghi transaction, xóa cache và `st.rerun()`. Timestamp chạy ETL và ngày cập nhật nguồn được trình bày riêng. Nếu thất bại, ứng dụng hiển thị lỗi và tiếp tục sử dụng snapshot cũ.

**Mặc định: cập nhật từ file.** Thay các CSV cùng schema trong `data/raw/`, rồi bấm nút. Chạy lại cùng dữ liệu không nhân đôi bảng; lịch sử ghi thêm một lần thực thi.

**Tùy chọn: nguồn CSV qua HTTPS.** Bộ dữ liệu không cung cấp URL/API/HTML xuất xứ nên dự án không giả lập crawler trực tiếp Fmarket hoặc website ngân hàng. `scraper.py` hỗ trợ endpoint trả về CSV cùng schema, với timeout, giới hạn 30 MB/file và kiểm tra dữ liệu trước khi lưu. Sao chép `sources.example.json` thành `sources.json`, điền URL thật cho các khóa cần tải; giá trị `null` dùng file cục bộ.

```powershell
$env:INVEST_SOURCES_CONFIG = 'D:\VSF\NTTT\BTL\sources.json'
python -m streamlit run app.py
# Hoặc chạy pipeline riêng:
python -m src.pipeline --sources-config sources.json
```

Endpoint phải trả CSV, không phải trang HTML đăng nhập. Kết nối HTTPS được kiểm thử bằng phản hồi giả lập trong unit test; chưa có endpoint nguồn thật để xác minh. Dữ liệu tải về đi qua staging và lưu kết quả vào DB, không ghi đè bản CSV gốc. SHA-256 từng đầu vào được lưu cùng lịch sử để đối chiếu.

## Quy tắc dữ liệu và công thức

Các cột tỷ lệ lưu theo đơn vị phần trăm: `6.05` nghĩa là `6,05%`. SQLite lưu ngày ISO dạng TEXT; khi đọc về Python đổi lại datetime. HTML được bỏ, dấu phẩy thập phân được chuẩn hóa, dấu `-` và giá trị không hợp lệ trở thành NULL. Cột chuỗi gốc lãi suất/CPI được giữ để kiểm toán.

| Chỉ số | Cách tính và giới hạn |
|---|---|
| Normalized NAV | `100 × NAV(t)/NAV(đầu)`; gốc là ngày quan sát đầu của từng quỹ trong cửa sổ |
| Lợi nhuận giai đoạn | `(NAV(cuối)/NAV(đầu) − 1) × 100` |
| CAGR | `((NAV(cuối)/NAV(đầu))^(365.25/số ngày) − 1) × 100`; dưới 2 ngày quan sát là NULL |
| Drawdown | `(NAV/đỉnh NAV đã quan sát − 1) × 100`; không suy diễn giá giữa các quan sát |
| Return 1M/3M/6M/12M | Giá tại hoặc trước ngày đích lùi tương ứng số tháng; lệch tối đa 14 ngày. Có thể dùng lịch sử trước ngày bắt đầu sidebar |
| Real Return 12M xấp xỉ | `Return 12M − CPI YoY cùng tháng` |
| Fisher 12M | `((1+r/100)/(1+i/100) − 1) × 100` |
| Tích lũy ngân hàng | `vốn × (1+lãi suất/100)^số năm`; lãi suất cố định, lãi kép hàng năm; phân số năm theo lãi kép |

Không lấy lợi nhuận lũy kế nhiều năm trừ CPI YoY một năm. CPI tháng là đối chiếu hồi cứu, không bảo đảm có sẵn tại ngày NAV. Phí quản lý không phải thước đo rủi ro: scatter dùng trục phí theo đặc tả, có tooltip mức rủi ro và chú thích. Không tự trừ thêm phí quản lý khỏi NAV. Mô phỏng chưa gồm thuế/phí giao dịch, điều kiện số dư ưu đãi hoặc rút trước hạn.

## Chất lượng của bộ CSV hiện có

- 5 quỹ, 4.871 dòng NAV thô. Loại 10 dòng trùng hoàn toàn; cách ly 18 dòng thuộc 9 khóa mâu thuẫn, còn **4.843 NAV** hợp lệ. Bảng `rejected_rows` giữ nội dung bị cách ly, không tự chọn một giá.
- 29 ngân hàng, 45 dòng ở dạng rộng (29 OTC, 16 Online). Chuyển sang **405 dòng kỳ hạn**, giữ lãi suất thiếu dưới dạng NULL.
- Cột `Kỳ hạn gửi tiết kiệm (tháng)` có giá trị giống lãi không kỳ hạn, trong khi các tiêu đề sau có dấu hiệu lệch. Không đủ chứng cứ để dịch cột: giữ nhãn nguồn, lưu `unmapped_rate`, cảnh báo trên giao diện và không dùng cột này làm kỳ hạn.
- 82 tháng CPI; 1 tháng thiếu MoM. Giữ trạng thái `Chính thức`/`Số liệu sơ bộ`, không dựng chỉ số giá lũy kế đầy đủ từ YoY.
- Snapshot lãi suất không thể chứng minh mức lãi suất lịch sử 2020–2026. Các so sánh ngân hàng chỉ là bài mô phỏng với dữ liệu theo nhãn nguồn.
- Không hard-code các số minh họa như VESAF +153,48%, 6,13% hay CPI 2,81% trong logic. Kết quả được tính từ CSV và thay đổi theo bộ lọc.

## SQLite

| Bảng | Nội dung |
|---|---|
| `fund_info` | Danh mục, phí, mức rủi ro, return snapshot nguồn |
| `fund_nav` | NAV sạch, loại quỹ, Base 100, return, drawdown, CPI và real return |
| `fund_holdings` | Cơ cấu tài sản và ngày snapshot |
| `bank_rates` | Lãi suất dạng dài, kỳ hạn, kênh gửi, timestamp và giá trị nguồn |
| `macro_cpi` | Tháng, CPI YoY/MoM, trạng thái và chuỗi nguồn |
| `quality_report` | Số dòng thiếu, trùng, mâu thuẫn và cảnh báo |
| `rejected_rows` | Dòng lỗi/cách ly, lý do và nội dung JSON |
| `update_history` | Thời điểm UTC+7, chế độ thu thập, SHA-256 và số dòng |

Toàn bộ thay đổi bảng và lịch sử nằm trong một transaction `BEGIN IMMEDIATE`; khóa NAV/quỹ/CPI có unique index. Kết nối được đóng rõ ràng để không giữ khóa file trên Windows.

## Notebook để báo cáo

Mở `notebooks/01_eda_and_mining.ipynb` bằng VS Code Jupyter hoặc JupyterLab, chọn kernel của môi trường đã cài requirements. Notebook đi từ khám phá schema, minh họa lỗi thật, giải thích quyết định làm sạch, đến đồ thị Base 100, phân phối/tương quan lợi nhuận tháng, biên Pareto CAGR–drawdown và sức mua. Kết luận tính trực tiếp từ dữ liệu; notebook kiểm chứng lưu/đọc SQLite bằng DB tạm.

Gợi ý thuyết trình: mở bảng lỗi và giải thích vì sao không tùy tiện sửa kỳ hạn; trình bày Base 100; đọc kết quả khai phá; cuối cùng đổi một bộ lọc và chạy nút ETL trên Streamlit để thể hiện hai tầng dùng chung logic.
