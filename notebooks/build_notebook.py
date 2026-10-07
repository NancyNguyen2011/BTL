"""Tạo lại notebook trình bày từ các ô Markdown/code; chạy từ project root."""
from pathlib import Path

import nbformat as nbf

cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text):
    cells.append(nbf.v4.new_code_cell(text))


md("""# Phòng lab: EDA & Data Mining hiệu quả đầu tư
**Sinh viên: NTTT~B23DCKD069**

Quy trình: **Khám phá → Làm sạch → Kết hợp → Tạo chỉ số → Khai phá insight → SQLite**.

Câu hỏi nghiên cứu: quỹ nào tăng trưởng tốt trong dữ liệu quan sát? Mức sụt giảm đi kèm là bao nhiêu? Lợi nhuận 12 tháng có vượt CPI YoY cùng kỳ không?

Notebook này dùng đúng các hàm sẽ chạy trong nút cập nhật Streamlit. Các nhận xét là kết quả phân tích bộ CSV được cung cấp, không xác nhận tính chính xác của nguồn ngoài.""")
code("""from pathlib import Path
import sys
ROOT = Path.cwd() if (Path.cwd() / 'src').exists() else Path.cwd().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
import plotly.express as px
from IPython.display import display
from src.cleaner import read_raw, clean_data, parse_number
from src.transformer import transform_data, period_summary
from src.pipeline import run_pipeline
from src.database import load_database
pd.set_option('display.max_columns', 20)
raw = read_raw(ROOT / 'data/raw')""")
md("""## 1. Khám phá dữ liệu và đơn vị quan sát
Trước khi tính toán, em xác định khóa: `(fund_id, ngày)` cho NAV; `(ngân hàng, hình thức, kỳ hạn, thời điểm quét)` cho lãi suất; tháng cho CPI. NAV có tần suất quan sát không đều nên không mặc định mọi bản ghi là một ngày giao dịch liên tiếp.

`raw_csv/` là bản ban đầu của đề bài; `data/raw/` là đầu vào vận hành. Năm file được đọc ở dạng chuỗi để nhìn thấy HTML, dấu phẩy thập phân và ô thiếu trước khi ép kiểu.""")
code("""inventory = pd.DataFrame([
    {'Bảng': name, 'Dòng': len(df), 'Cột': len(df.columns),
     'Ô thiếu': int(df.isna().sum().sum()), 'Trùng hoàn toàn': int(df.duplicated().sum())}
    for name, df in raw.items()
])
display(inventory)
for name, frame in raw.items():
    print(name)
    display(frame.head(3))""")
md("""## 2. Chẩn đoán chất lượng trước khi sửa
Em quan sát lãi suất có thẻ `<span>`, dấu phẩy thập phân và dấu `-`. Cột **Kỳ hạn gửi tiết kiệm (tháng)** lại chứa các số 0,10 / 0,20, trong khi cột Không Kỳ Hạn chứa mức vài phần trăm: đây là dấu hiệu tiêu đề lệch khi cào dữ liệu. Không có HTML nguồn hay sơ đồ ánh xạ đáng tin cậy nên em giữ nhãn kỳ hạn gốc, lưu cột không rõ kỳ hạn riêng, và cảnh báo mọi kết quả ngân hàng cần xác minh.

Giá NAV trùng khóa nhưng khác giá trị không được lấy trung bình hoặc chọn tùy ý: cả hai bản sẽ được cách ly. Dòng trùng hoàn toàn chỉ giữ một. CPI MoM thiếu được giữ NULL, không điền 0.""")
code("""bank_raw = raw['bank_rates']
html_rows = bank_raw.apply(lambda col: col.str.contains('<[^>]+>', na=False)).any(axis=1)
display(bank_raw.loc[html_rows].head())
nav_raw = raw['fund_nav']
display(nav_raw[nav_raw.duplicated(['fund_id', 'navDate'], keep=False)].head(12))
display(raw['macro_cpi'][raw['macro_cpi'].cpi_mom_str.isna()])
examples = ['<span class="text-green">6,05</span>', '-0,21%', '-', '1.234,56']
display(pd.DataFrame({'Thô': examples, 'Sau parse_number': [parse_number(v) for v in examples]}))""")
md("""## 3. Làm sạch và kết hợp (Stage 3)
Em tách việc đọc file khỏi biến đổi để dễ kiểm thử. Ngày được ép `datetime`, NAV và tỷ lệ được ép `float`; giá NAV không dương bị loại. Kết hợp NAV và metadata theo `fund_id` với kiểm tra `many_to_one` để tránh nhân bản số dòng. CPI gắn theo tháng để đối chiếu hồi cứu, không được hiểu là đã công bố tại ngày giao dịch.

Báo cáo dưới đây ghi số dòng loại/cách ly và thiếu dữ liệu, thay vì khẳng định dữ liệu đã hoàn hảo.""")
code("""clean = clean_data(raw)
display(clean['quality_report'])
display(clean['rejected_rows'])
display(clean['fund_nav'].dtypes.to_frame('Kiểu dữ liệu'))
assert not clean['fund_nav'].duplicated(['fund_id', 'date']).any()
assert clean['fund_nav'].nav.gt(0).all()
print('Số NAV dùng được:', len(clean['fund_nav']))""")
md("""## 4. Tạo chỉ số có cùng cơ sở so sánh (Stage 4)
**Normalized NAV = NAV(t) / NAV(gốc) × 100.** Các quỹ có NAV tuyệt đối khác nhau nên cần chung thang tăng trưởng. Ngày gốc là ngày quan sát đầu của từng quỹ trong giai đoạn chọn, không giả định có giá ngày 01/01/2020.

**CAGR = (NAV cuối / NAV đầu)^(365,25 / số ngày) − 1.** Drawdown đo mức giảm từ đỉnh đã quan sát. Lợi nhuận 12M lấy giá tại hoặc trước mốc 12 tháng, cho phép độ trễ tối đa 14 ngày; thiếu lịch sử thì để trống.

**Lợi nhuận thực xấp xỉ = Return 12M − CPI YoY cùng tháng.** Fisher chính xác hơn: `(1+r)/(1+i)−1`. Không trừ CPI YoY một năm khỏi lợi nhuận lũy kế nhiều năm.""")
code("""tables = transform_data(clean)
nav = tables['fund_nav']
summary = period_summary(nav).sort_values('total_return', ascending=False)
display(summary.round(2))
assert np.allclose(nav.groupby('fund_id').first().normalized_nav, 100)
px.line(nav, x='date', y='normalized_nav', color='symbol',
        title='Tăng trưởng chuẩn hóa Base 100').show()""")
md("""## 5. EDA trực quan: phân phối, tương quan và cơ cấu
Em dùng lợi nhuận **tháng** để giảm ảnh hưởng tần suất NAV không đều. Chỉ tính khi có NAV của hai tháng liền nhau; không forward-fill các tháng thiếu. Tương quan là mô tả đồng biến, không chứng minh quan hệ nhân quả. Khi dữ liệu có ít quỹ, xếp hạng và ma trận tương quan dễ giải thích hơn một mô hình học máy không có mục tiêu rõ ràng.""")
code("""monthly_prices = nav.pivot(index='date', columns='symbol', values='nav').resample('ME').last()
monthly_returns = monthly_prices.pct_change(fill_method=None) * 100
display(monthly_returns.describe().round(2))
px.imshow(monthly_returns.corr(), text_auto='.2f', zmin=-1, zmax=1,
          color_continuous_scale='RdBu_r', title='Tương quan lợi nhuận tháng').show()
px.box(monthly_returns.melt(var_name='Quỹ', value_name='Lợi nhuận tháng (%)').dropna(),
       x='Quỹ', y='Lợi nhuận tháng (%)', title='Phân phối lợi nhuận tháng').show()
display(clean['fund_holdings'].pivot_table(index='symbol', columns='asset_type', values='asset_percent', aggfunc='last').fillna(0))""")
md("""## 6. Data Mining: xếp hạng và phát hiện đánh đổi tăng trưởng–sụt giảm
Em khai phá quy luật theo nhóm quỹ và dùng **biên Pareto**: một quỹ bị trội nếu có quỹ khác vừa CAGR cao hơn hoặc bằng, vừa sụt giảm tối đa ít nghiêm trọng hơn hoặc bằng, với ít nhất một tiêu chí tốt hơn. Đây là cách sàng lọc mô tả trên mẫu hiện có, không phải khuyến nghị mua quỹ.

Các ngày NAV mâu thuẫn đã cách ly có thể ảnh hưởng biến động. Kết quả drawdown chỉ đo trên các quan sát còn lại, không khẳng định đã ghi nhận mọi đáy thị trường.""")
code("""mining = summary.merge(clean['fund_info'][['symbol', 'fund_type']], on='symbol')
mining['pareto'] = [not (((mining.cagr >= row.cagr) &
                          (mining.max_drawdown >= row.max_drawdown) &
                          ((mining.cagr > row.cagr) | (mining.max_drawdown > row.max_drawdown))).any())
                    for row in mining.itertuples()]
display(mining[['symbol', 'fund_type', 'total_return', 'cagr', 'max_drawdown', 'pareto']].round(2))
px.scatter(mining, x='max_drawdown', y='cagr', color='fund_type', text='symbol',
           symbol='pareto', title='Tăng trưởng và mức giảm từ đỉnh quan sát').show()
leader = mining.iloc[0]
print(f'Quỹ dẫn đầu tổng lợi nhuận trong dữ liệu: {leader.symbol}, {leader.total_return:.2f}%.')
print('Các quỹ trên biên Pareto:', ', '.join(mining.loc[mining.pareto, 'symbol']))""")
md("""## 7. Insight sức mua: cùng tháng, cùng kỳ 12M
Để tránh so sánh lệch thời điểm, em chọn tháng gần nhất có lợi nhuận 12M của tất cả quỹ, và luôn hiển thị trạng thái CPI sơ bộ/chính thức. Lợi nhuận thực âm nghĩa là mức tăng NAV trong kỳ không bù CPI YoY; không có nghĩa NAV nhất thiết giảm tuyệt đối.""")
code("""monthly = nav.sort_values('date').groupby(['symbol', 'month']).tail(1)
valid = monthly.dropna(subset=['real_return_12m'])
counts = valid.groupby('month').symbol.nunique()
common = counts[counts == nav.symbol.nunique()]
if not common.empty:
    latest = valid[valid.month == common.index.max()]
    display(latest[['symbol', 'month', 'return_12m_nav', 'cpi_yoy', 'cpi_status', 'real_return_12m', 'real_return_fisher_12m']].round(2))
    px.bar(latest.sort_values('real_return_12m'), x='symbol', y='real_return_12m',
           color='fund_type', title='Lợi nhuận thực 12M xấp xỉ ở tháng chung gần nhất').show()
    print('Số quỹ vượt CPI:', int((latest.real_return_12m > 0).sum()), '/', len(latest))
else:
    print('Chưa có tháng chung đủ lịch sử cho tất cả quỹ.')""")
md("""## 8. Đóng gói vận hành và lưu SQLite
Notebook chứng minh phép biến đổi; `src/cleaner.py` và `src/transformer.py` là nơi giữ logic dùng chung. Pipeline ghi toàn bộ snapshot và lịch sử cập nhật trong một transaction. Nếu đọc nguồn, schema hoặc ghi dữ liệu lỗi, snapshot trước vẫn dùng được.

Để thí nghiệm không thay CSDL của ứng dụng, ô sau chạy pipeline vào CSDL tạm, rồi đọc lại để đối chiếu.""")
code("""import tempfile
with tempfile.TemporaryDirectory() as temporary:
    db = Path(temporary) / 'lab.db'
    run = run_pipeline(db_path=db)
    loaded = load_database(db)
    assert len(loaded['fund_nav']) == len(nav)
    display(pd.DataFrame([{'Bảng SQLite': name, 'Dòng': len(frame)} for name, frame in loaded.items()]))
    print('Chế độ thu thập:', run['mode'])""")
md("""## 9. Kết luận và giới hạn
- Kết luận về quỹ dẫn đầu và sức mua được sinh từ dữ liệu ở các ô trên, không hard-code số ví dụ trong bản thiết kế.
- NAV có khóa trùng mâu thuẫn; các dòng đó được cách ly và giữ trong bảng kiểm toán.
- Snapshot lãi suất không đại diện lịch sử 2020–2026; tiêu đề kỳ hạn cần đối chiếu HTML nguồn. Chỉ sử dụng làm kịch bản giả định có ghi nhãn.
- CPI có số sơ bộ và thiếu MoM; chưa đủ căn cứ dựng sức mua tích lũy toàn kỳ từ chỉ số giá tháng.
- Phí quản lý và thông tin quỹ là snapshot không có ngày hiệu lực. Return trong factsheet có thể khác lợi nhuận tự tính vì thời điểm/chuỗi NAV khác nhau. Không trừ thêm phí quản lý lần nữa vào NAV khi chưa rõ quy ước nguồn.
- Bước tiếp theo khi có nguồn gốc rõ ràng: sửa ánh xạ kỳ hạn, bổ sung lãi suất theo thời gian và ngày công bố CPI để phân tích không nhìn trước tương lai.""")

notebook = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}})
nbf.write(notebook, Path(__file__).with_name("01_eda_and_mining.ipynb"))
