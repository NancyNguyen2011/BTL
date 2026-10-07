Dưới đây là **Bản thiết kế Bố cục Chi tiết (Layout Architecture Blueprint)** hoàn chỉnh cho ứng dụng **Streamlit** của bạn. Bản thiết kế này tập trung hoàn toàn vào **cấu trúc giao diện, tư duy lựa chọn biểu đồ trực quan (Data Visualization Strategy), cơ chế tương tác và các Insight đầu tư cần giải đáp**, không chứa mã code theo đúng yêu cầu của bạn.

---

# 📐 BẢN THIẾT KẾ BỐ CỤC CHI TIẾT ỨNG DỤNG STREAMLIT

## 1. TIÊU ĐỀ VÀ THÔNG TIN SINH VIÊN (HEADER SECTION)

* **Tiêu đề chính trang web (App Title)**: 
  `📊 BÁO CÁO PHÂN TÍCH VÀ SO SÁNH HIỆU QUẢ ĐẦU TƯ: CHỨNG CHỈ QUỸ (FMARKET) VS LÃI SUẤT NGÂN HÀNG VS CHỈ SỐ LẠM PHÁT (CPI)`
* **Thông tin Sinh viên (Sub-header Badge)**:
  `🎓 Sinh viên thực hiện: NTTT~B23DCKD069`
* **Khung Theo dõi Trạng thái 3 Nguồn Dữ liệu (3-Source Data Update Tracker)**:
  * **Visual**: Hiển thị 3 thẻ Badge trạng thái nằm ngang ngay dưới phần tiêu đề:
    * 🟢 **Nguồn 1 (Fmarket - CCQ)**: Cập nhật dữ liệu NAV daily từ `01/2020` đến `10/2026`.
    * 🟢 **Nguồn 2 (Lãi suất Ngân hàng)**: Cập nhật dữ liệu lãi suất của 29 ngân hàng (Quét ngày `06/10/2026`).
    * 🟢 **Nguồn 3 (Macro CPI)**: Cập nhật chỉ số lạm phát YoY/MoM từ `01/2020` đến `Tháng 10/2026`.
  * **Tính năng Tương tác Chi tiết (Source Status Expander)**:
    * Nút ấn mở rộng **"🔍 Chi tiết Trạng thái Dữ liệu & Lịch sử Cập nhật"**. Khi người dùng nhấp vào, màn hình mở ra bảng tổng hợp:
      * **File Fmarket**: Số lượng ngày giao dịch, mã quỹ khả dụng (tự động nhận diện từ 5 đến 7+ quỹ).
      * **File Ngân hàng**: Thời điểm quét dữ liệu gần nhất, ngân hàng có lãi suất cao nhất.
      * **File CPI**: Số lượng tháng dữ liệu (82 tháng) và phân định rõ dữ liệu `Chính thức` vs `Số liệu sơ bộ`.

---

## 2. THANH BỘ LỌC TOÀN CỤC (GLOBAL SIDEBAR CONTROLS)

Thanh Sidebar bên trái màn hình giúp điều khiển dữ liệu hiển thị trên cả 4 Tab:

1. **Thanh trượt Chọn Khoảng thời gian (Date Range Slider)**: Chọn giai đoạn từ `2020` đến `2026` (Mặc định chọn toàn bộ 2020 - 2026).
2. **Bộ chọn Loại Quỹ (Fund Type Filter)**: Tất cả / Quỹ Cổ phiếu / Quỹ Trái phiếu / Quỹ Cân bằng.
3. **Ô nhập Vốn Đầu tư Ban đầu (Initial Capital Input)**: Cho phép người dùng nhập số tiền đầu tư giả định (VD: `100.000.000 VNĐ`).
4. **Bộ chọn Ngân hàng & Kỳ hạn So sánh**: Chọn danh sách ngân hàng cụ thể và kỳ hạn gửi (6 tháng, 12 tháng, 24 tháng).

---

## 3. CHI TIẾT CẤU TRÚC 4 TAB CHỨC NĂNG & DẠNG BIỂU ĐỒ TRỰC QUAN

---

### 📈 **TAB 1: TỔNG QUAN DASHBOARD & TOP DANH MỤC HIỆU QUẢ NHẤT**

* **Mục tiêu trả lời câu hỏi**: *Danh mục/CCQ nào đang dẫn đầu về hiệu suất hiện tại và trong cả giai đoạn 2020–2026? Tổng quan thị trường ra sao?*
* **Bố cục Visual & Biểu đồ trực quan**:
  1. **Khối Thẻ Chỉ số KPI (KPI Summary Metrics)**:
     * **Top CCQ Tăng trưởng cao nhất**: `VESAF` (+153.48% từ 2020) hoặc `DCDS` (+129.01%).
     * **Top Lãi suất Ngân hàng 12M cao nhất**: `PVcomBank` (9.0%/năm).
     * **Lạm phát CPI YoY gần nhất**: `2.81%` (Tháng 10/2026).
  2. **Biểu đồ 1: Đường Tăng trưởng Lũy kế Chuẩn hóa (Normalized NAV Growth Line Chart - Baseline 100%)**:
     * *Dạng biểu đồ*: **Multi-Line Chart** (Plotly Interactive).
     * *Cách thể hiện*: Chuẩn hóa mốc giá trị của tất cả các quỹ về mốc **100 điểm** vào tháng 1/2020.
     * *Insight giải đáp*: Giúp so sánh công bằng tốc độ tăng trưởng giữa các quỹ bất kể giá NAV ban đầu khác nhau. Nhìn rõ chu kỳ sóng của nhóm quỹ cổ phiếu (`VESAF`, `DCDS`, `VCBF-BCF`) so với đường tăng trưởng ổn định, ít biến động của quỹ trái phiếu (`VFF`, `DCBF`).
  3. **Biểu đồ 2: Cột Xếp hạng Tỷ suất Sinh lời Tổng thể (Sorted Bar Chart)**:
     * *Dạng biểu đồ*: **Horizontal Bar Chart** (Biểu đồ cột nằm ngang xếp hạng từ cao xuống thấp).
     * *Cách thể hiện*: Cột hiển thị % lợi nhuận tổng cộng kể từ khi thành lập (`Return Since Inception`) hoặc 12 tháng gần nhất (`Return 12M`).
     * *Insight giải đáp*: Xác định ngay lập tức vị thế Top 1, Top 2, Top 3 danh mục đầu tư sinh lời tốt nhất.

---

### 🍕 **TAB 2: CƠ CẤU PHÂN BỔ TÀI SẢN & SO SÁNH CHI TIẾT CCQ**

* **Mục tiêu trả lời câu hỏi**: *Cơ cấu đầu tư của từng quỹ gồm những gì (Cổ phiếu, Trái phiếu, Tiền mặt)? So sánh chi tiết các quỹ về rủi ro, phí quản lý và hiệu suất các kỳ hạn?*
* **Bố cục Visual & Biểu đồ trực quan**:

  * **PHẦN A: DRILL-DOWN CHI TIẾT CƠ CẤU TỪNG QUỸ (Single Fund Portfolio Breakdown)**:
    * **Thanh chọn quỹ (Selectbox)**: Cho phép chọn riêng 1 quỹ để soi chi tiết (VD: chọn `VESAF`, `VCBF-BCF`, `VFF`...).
    * **Biểu đồ 1: Biểu đồ Tròn / Vành khăn Cơ cấu Tài sản (Donut / Pie Chart - Asset Allocation)**:
      * *Dạng biểu đồ*: **Donut Chart** có chú thích tỷ lệ % chi tiết.
      * *Cách thể hiện*: Chia rõ tỷ trọng % các lớp tài sản (`Cổ phiếu`, `Trái phiếu`, `Tiền & tương đương tiền`, `Tài sản khác`).
      * *Insight giải đáp*: 
        * **VESAF**: 88.91% Cổ phiếu | 10.82% Tiền mặt | 0.27% Khác (Quỹ tăng trưởng mạnh).
        * **VCBF-BCF**: 94.75% Cổ phiếu | 4.79% Tiền mặt (Tỷ lệ cổ phiếu rất cao).
        * **VFF**: 76.42% Trái phiếu | 23.58% Tiền mặt (Quỹ an toàn, thu nhập cố định).
    * **Thẻ Thông tin Kỹ thuật Quỹ (Fund Factsheet Card)**: Hiển thị Phí quản lý (%), Mức độ rủi ro, Giá trị mua tối thiểu, và Ngày cập nhật danh mục (`09/09/2026`).

  * **PHẦN B: SO SÁNH ĐA QUỸ (Multi-Fund Matrix Comparison)**:
    * **Biểu đồ 2: Cột Nhóm Hiệu suất theo Kỳ hạn (Grouped Bar Chart)**:
      * *Dạng biểu đồ*: **Grouped Bar Chart** (Mỗi quỹ có một nhóm cột đại diện cho `Return 1M`, `3M`, `6M`, `12M`).
      * *Insight giải đáp*: Đánh giá xem quỹ nào đang có phong độ tốt trong ngắn hạn (1–3 tháng) so với dài hạn (12 tháng). Tự động linh hoạt hiển thị khi danh sách mở rộng từ 5 đến 7+ quỹ.
    * **Biểu đồ 3: Tán sắc Rủi ro vs Lợi nhuận (Scatter Plot - Risk vs Return Matrix)**:
      * *Dạng biểu đồ*: **Scatter Plot** 4 phần tư.
      * *Trục X*: Phí quản lý (%) hoặc Mức độ rủi ro.
      * *Trục Y*: Tỷ suất sinh lời kỳ vọng (Return 12M).
      * *Insight giải đáp*: Định vị quỹ nằm ở góc "Rủi ro cao - Lợi nhuận cao" hay "Rủi ro thấp - Lợi nhuận ổn định".

---

### 🏦 **TAB 3: SO SÁNH CCQ VS LÃI SUẤT TIẾT KIỆM NGÂN HÀNG**

* **Mục tiêu trả lời câu hỏi**: *Nên gửi ngân hàng hay đầu tư CCQ? Tốc độ tích lũy tài sản giữa 2 kênh chênh lệch bao nhiêu sau 6 năm?*
* **Bố cục Visual & Biểu đồ trực quan**:
  1. **Biểu đồ 1: Mô phỏng Tích lũy Tài sản (Investment Growth Simulation Chart)**:
     * *Dạng biểu đồ*: **Area / Line Chart** đường vùng chồng lặp.
     * *Cách thể hiện*: So sánh số tiền thu về từ số vốn ban đầu (nhập ở Sidebar, VD: 100 triệu VNĐ) qua từng năm:
       * *Đường 1*: Số tiền thực tế khi đầu tư vào CCQ (Lấy theo NAV thực tế).
       * *Đường 2*: Số tiền thu về khi gửi Ngân hàng lãi suất trung bình ngành (~6.13%/năm, lãi nhập gốc hàng năm).
       * *Đường 3*: Số tiền thu về khi gửi Ngân hàng lãi suất cao nhất (`PVcomBank` 9.0%/năm).
     * *Insight giải đáp*: Thấy rõ hiệu ứng lãi kép và chênh lệch tài sản tuyệt đối (VD: 100 triệu gửi ngân hàng sau 6 năm lên ~145-160 triệu, trong khi đầu tư CCQ cổ phiếu đạt ~220-250 triệu VNĐ).
  2. **Biểu đồ 2: Xếp hạng Lãi suất 29 Ngân hàng (Horizontal Sorted Bar Chart)**:
     * *Dạng biểu đồ*: **Horizontal Bar Chart** có phân màu theo hình thức gửi (Gửi Online vs Gửi tại quầy OTC).
     * *Insight giải đáp*: Lọc và tìm ngay ngân hàng có lãi suất cao nhất cho kỳ hạn 6M, 12M, 24M.
  3. **Bộ Tính toán Lợi nhuận Tương tác (Interactive Investment Calculator)**:
     * Người dùng chọn 1 Ngân hàng + 1 Quỹ CCQ + Số tiền gửi + Số năm đầu tư.
     * *Kết quả trả về*: Bảng so sánh lợi nhuận chênh lệch tuyệt đối bằng tiền VNĐ và tỷ lệ phần trăm (%).

---

### 📉 **TAB 4: TỶ SUẤT SINH LỜI THỰC TẾ VS CHỈ SỐ LẠM PHÁT CPI**

* **Mục tiêu trả lời câu hỏi**: *Kênh đầu tư nào đánh bại lạm phát CPI và bảo vệ sức mua thực tế cho nhà đầu tư?*
* **Bố cục Visual & Biểu đồ trực quan**:
  1. **Biểu đồ 1: Kết hợp Cột & Đường (Combo Bar & Line Chart)**:
     * *Dạng biểu đồ*: **Dual-Axis Combo Chart** (Biểu đồ 2 trục tung).
     * *Trục 1 (Cột - Bar Chart)*: Chỉ số lạm phát CPI YoY (%) theo từng tháng từ 01/2020 đến 10/2026.
     * *Trục 2 (Đường - Line Chart)*: Tỷ suất sinh lời bình quân năm của CCQ và Lãi suất tiết kiệm ngân hàng cùng thời kỳ.
     * *Insight giải đáp*: Nhìn thấy trực quan các giai đoạn lạm phát tăng cao (VD: Đầu năm 2020 CPI đạt 4.29%) và so sánh trực tiếp với lãi suất ngân hàng / lợi nhuận CCQ thời điểm đó.
  2. **Biểu đồ 2: Lợi nhuận Thực tế (Real Return Diverging Bar Chart)**:
     * *Công thức*: \\(\text{Lợi nhuận thực} = \text{Tỷ suất sinh lời danh nghĩa} - \text{Chỉ số Lạm phát CPI YoY}\\).
     * *Dạng biểu đồ*: **Diverging Bar Chart** (Biểu đồ cột phân kỳ mốc 0%).
     * *Insight giải đáp*:
       * **Gửi ngân hàng**: Mang lại lợi nhuận thực dương nhẹ (+2.0% đến +3.5%/năm), đóng vai trò bảo vệ tài sản khỏi trượt giá.
       * **CCQ cổ phiếu**: Mang lại lợi nhuận thực vượt trội (+10% đến +18%/năm trên bình quân chu kỳ dài hạn 2020–2026), là kênh gia tăng tài sản và chống lạm phát hiệu quả nhất.

---

## 4. BẢNG TỔNG HỢP MA TRẬN BIỂU ĐỒ VÀ CÂU HỎI KINH DOANH

| Tab Chức năng | Dạng Biểu đồ Trực quan | Mục đích & Câu hỏi Giải đáp |
| :--- | :--- | :--- |
| **Tab 1: Tổng quan** | **Normalized Line Chart** (Mốc 100%) | CCQ nào tăng trưởng tốt nhất từ 2020 đến nay? Tốc độ tăng trưởng qua các chu kỳ ra sao? |
| **Tab 1: Tổng quan** | **Sorted Horizontal Bar Chart** | Xếp hạng Top 1, Top 2, Top 3 danh mục đầu tư đạt lợi nhuận cao nhất. |
| **Tab 2: Cơ cấu CCQ** | **Donut Chart** (Pie Chart vành khăn) | Cơ cấu phân bổ tài sản của 1 quỹ gồm bao nhiêu % Cổ phiếu, Trái phiếu, Tiền mặt? |
| **Tab 2: Cơ cấu CCQ** | **Grouped Bar Chart** | So sánh hiệu suất ngắn hạn (1M, 3M, 6M) và dài hạn (12M) giữa tất cả các quỹ (linh hoạt 5-7 quỹ). |
| **Tab 2: Cơ cấu CCQ** | **Scatter Plot** (Risk vs Return) | Quỹ nào thuộc nhóm "Rủi ro cao - Lợi nhuận cao" vs "Rủi ro thấp - Lợi nhuận ổn định"? |
| **Tab 3: CCQ vs Ngân hàng** | **Investment Growth Area/Line Chart** | Tích lũy tài sản sau 6 năm chênh lệch bao nhiêu triệu VNĐ giữa gửi ngân hàng vs đầu tư CCQ? |
| **Tab 3: CCQ vs Ngân hàng** | **Horizontal Sorted Bar Chart** | Top ngân hàng nào có lãi suất tiết kiệm cao nhất cho kỳ hạn 6M, 12M, 24M (Online vs OTC)? |
| **Tab 4: CCQ/Ngân hàng vs CPI** | **Dual-Axis Combo Chart** (Bar & Line) | Tỷ suất sinh lời của CCQ và Ngân hàng biến động như thế nào so với diễn biến lạm phát CPI? |
| **Tab 4: CCQ/Ngân hàng vs CPI** | **Diverging Bar Chart** (Real Return) | Kênh đầu tư nào mang lại Lợi nhuận thực (Real Return) dương và đánh bại lạm phát? |

---

💡 Bản thiết kế giao diện này đã bao quát toàn bộ yêu cầu về tên sinh viên, cấu trúc 4 tab, hiển thị trạng thái 3 nguồn dữ liệu, biểu đồ tròn cơ cấu tài sản từng quỹ, và các loại biểu đồ so sánh tối ưu nhất. 

Bạn có muốn điều chỉnh hoặc bổ sung thêm góc nhìn phân tích nào cho từng Tab không?