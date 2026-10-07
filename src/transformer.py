"""Stage 4: chỉ số dựa trên NAV quan sát, không điền ngược dữ liệu tương lai."""
import numpy as np
import pandas as pd


def normalize_nav(nav):
    result = nav.sort_values(["fund_id", "date"]).copy()
    first = result.groupby("fund_id").nav.transform("first")
    result["normalized_nav"] = result.nav / first * 100
    result["cumulative_return"] = result.normalized_nav - 100
    # Đây là lợi nhuận giữa hai lần quan sát, không giả định tất cả là daily.
    result["observation_return"] = result.groupby("fund_id").nav.pct_change(fill_method=None) * 100
    peak = result.groupby("fund_id").nav.cummax()
    result["drawdown"] = (result.nav / peak - 1) * 100
    return result


def trailing_returns(nav, months):
    """NAV tại hoặc trước mốc t-months, tối đa 14 ngày để tránh so sánh giá quá cũ."""
    output = pd.Series(np.nan, index=nav.index, dtype=float)
    for _, group in nav.groupby("fund_id"):
        group = group.sort_values("date")
        lookup = pd.DataFrame({"target": group.date - pd.DateOffset(months=months), "row": group.index})
        past = group[["date", "nav"]].rename(columns={"date": "past_date", "nav": "past_nav"})
        matched = pd.merge_asof(lookup.sort_values("target"), past, left_on="target", right_on="past_date",
                                direction="backward", tolerance=pd.Timedelta(days=14))
        output.loc[matched.row] = (nav.loc[matched.row, "nav"].to_numpy() / matched.past_nav.to_numpy() - 1) * 100
    return output


def transform_data(cleaned):
    tables = {name: frame.copy() for name, frame in cleaned.items()}
    nav = normalize_nav(tables["fund_nav"]).reset_index(drop=True)
    for months in (1, 3, 6, 12):
        nav[f"return_{months}m_nav"] = trailing_returns(nav, months)
    # CPI tháng là đối chiếu hồi cứu cùng tháng, không phải thông tin có sẵn tại ngày giao dịch.
    nav["month"] = nav.date.dt.to_period("M").dt.to_timestamp()
    cpi = tables["macro_cpi"][["date", "cpi_yoy", "cpi_mom", "status"]].rename(
        columns={"date": "month", "status": "cpi_status"})
    nav = nav.merge(cpi, on="month", how="left", validate="many_to_one")
    nav["real_return_12m"] = nav.return_12m_nav - nav.cpi_yoy
    nav["real_return_fisher_12m"] = ((1 + nav.return_12m_nav / 100) / (1 + nav.cpi_yoy / 100) - 1) * 100
    tables["fund_nav"] = nav
    return tables


def period_summary(nav):
    """Tính lại base 100, CAGR và drawdown cho đúng cửa sổ sidebar."""
    rows = []
    for symbol, group in normalize_nav(nav).groupby("symbol"):
        first, last = group.iloc[0], group.iloc[-1]
        years = (last.date - first.date).days / 365.25
        total = (last.nav / first.nav - 1) * 100
        rows.append({"symbol": symbol, "start": first.date, "end": last.date,
                     "total_return": total, "cagr": ((last.nav / first.nav) ** (1 / years) - 1) * 100 if years > 0 else np.nan,
                     "max_drawdown": group.drawdown.min(), "observations": len(group),
                     **{f"return_{m}m_nav": last.get(f"return_{m}m_nav", np.nan) for m in (1, 3, 6, 12)}})
    return pd.DataFrame(rows)


def bank_growth(capital, annual_rate, years):
    """Kịch bản lãi suất cố định, lãi nhập gốc hàng năm, phân số năm theo lãi kép."""
    return capital * (1 + annual_rate / 100) ** years
