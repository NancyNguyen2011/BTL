### 💡 Mô hình "2 Tầng Kiến trúc" (Dual-Layer Architecture)

Bạn sẽ trình bày với giảng viên rằng dự án của bạn có **2 tầng rõ ràng**:

1. **Tầng 1 - Phòng Lab Thử nghiệm (`notebooks/eda_and_etl_experiment.ipynb`)**:
   * **Vai trò**: Là nơi bạn "vật lộn" với dữ liệu thô ban đầu, phát hiện ra lỗi thẻ HTML, lỗi dấu phẩy `,`, lệch kiểu dữ liệu, thử nghiệm các công thức tính `Normalized NAV` hay `Real Return`.
   * **Mục đích nộp giảng viên**: Chứng minh tư duy phân tích cá nhân, lý do chọn cách làm sạch này mà không phải cách khác.
2. **Tầng 2 - Tự động hóa Thực thi (`src/pipeline/` & `app.py`)**:
   * **Vai trò**: Sau khi các hàm xử lý dữ liệu ở Tầng 1 đã chạy chuẩn xác, bạn đóng gói (refactor) các đoạn code đó thành các hàm Python (`.py`).
   * **Mục đích vận hành**: Khi người dùng ấn nút *"Cập nhật dữ liệu"* trên Streamlit, Streamlit sẽ gọi lại chính các hàm đã thử nghiệm thành công từ Tầng 1 để chạy tự động (Scrape ➔ Transform ➔ Save DB ➔ Visual).

---

### 📂 Cấu trúc Thư mục Dự án Thể hiện cho Giảng viên

Bạn hãy tổ chức thư mục mã nguồn theo chuẩn chuyên nghiệp như sau:

```text
project_root/
│
├── 📁 notebooks/                       # 👈 [TẦNG 1: DÀNH CHO GIẢNG VIÊN ĐÁNH GIÁ TƯ DUY]
│   └── 01_data_exploration_&_etl.ipynb # File Jupyter Notebook thử nghiệm từng bước kèm ghi chú Markdown
│
├── 📁 src/                             # 👈 [TẦNG 2: ĐÓNG GÓI MODULE TỰ ĐỘNG HÓA]
│   ├── scraper.py                      # Module cào dữ liệu mới (Fmarket, Bank rates, CPI)
│   ├── transformer.py                  # Module làm sạch & tạo chỉ số (chuyển từ notebook sang)
│   └── database.py                     # Module lưu trữ vào CSDL SQLite
│
├── 📁 data/
│   ├── raw/                            # Dữ liệu thô
│   └── processed/invest_analytics.db   # CSDL SQLite sau khi biến đổi
│
├── app.py                              # Màn hình Streamlit chính
└── README.md                           # Sơ đồ kiến trúc & Hướng dẫn thuyết minh
```

---

### 📝 Cách Thể hiện Trong File Jupyter Notebook (`.ipynb`) Để Giảng viên Thấy "Dấu Ấn Cá Nhân"

Trong file `.ipynb`, bạn hãy viết thêm các ô **Markdown giải thích tư duy** trước mỗi đoạn code. Giảng viên sẽ đọc phần Markdown này để đánh giá:

1. **Ghi rõ quan sát ban đầu**:
   * *Markdown ví dụ*: `"Khi soi dữ liệu thô từ file raw_bank_interest_rates.csv, em phát hiện lãi suất bị dính thẻ HTML <span class='text-green'>. Do đó em quyết định viết hàm Regex để lọc bỏ các thẻ này trước khi ép kiểu float."`*
2. **Giải thích lý do lựa chọn giải pháp**:
   * *Markdown ví dụ*: `"Dữ liệu NAV của các quỹ có giá trị ban đầu rất khác nhau (VCBF-BCF ~18,000 VNĐ, DCDS ~40,000 VNĐ). Nếu vẽ trực tiếp sẽ khó so sánh tốc độ tăng trưởng. Em tạo thêm chỉ số Normalized NAV quy về gốc 100 vào tháng 1/2020."`*
3. **Kết luận sau mỗi bước**:
   * *Markdown ví dụ*: `"Sau bước làm sạch, dữ liệu đã hết ô khuyết thiếu và được đóng gói thành hàm clean_data(). Hàm này sẽ được xuất sang file src/transformer.py để phục vụ nút bấm tự động trên Streamlit."`*

---

### ⚙️ Cách Thể hiện Chức năng Tự động hóa trên Màn hình Streamlit

Trên giao diện Streamlit, bạn thiết kế một nút bấm ở Sidebar hoặc ngay trên Banner trạng thái dữ liệu:

* **Nút bấm**: `🔄 Cập nhật Dữ liệu Mới (Scrape & ETL)`
* **Luồng chạy phía sau (Workflow)**:
  1. Người dùng bấm nút ➔ Streamlit gọi `scraper.py` để lấy dữ liệu mới nhất từ mạng/file.
  2. Streamlit gọi `transformer.py` (chứa đúng logic đã chứng minh trong file `.ipynb`) để làm sạch và tính toán lại các chỉ số.
  3. Ghi đè/Cập nhật vào CSDL SQLite (`invest_analytics.db`).
  4. Màn hình tự động làm mới (`st.rerun()`) và vẽ lại biểu đồ ngay lập tức.

---