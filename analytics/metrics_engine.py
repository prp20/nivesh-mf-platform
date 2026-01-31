import pandas as pd
import numpy as np
import warnings
from sqlalchemy.orm import Session

from backend.models.nav_data import NavData
from backend.models.benchmark_nav import BenchmarkNav
from backend.models.fund_metrics_snapshot import FundMetricsSnapshot
from backend.models.mutual_fund import MutualFund

# Suppress numpy RuntimeWarnings for NaN operations (we handle them explicitly)
warnings.filterwarnings('ignore', category=RuntimeWarning)


# ---------------- Configuration ----------------
TRADING_DAYS = 252
RISK_FREE_RATE_ANNUAL = 0.05  # 5% India G-Sec proxy
MIN_NAV_POINTS = 60           # minimum data required
EPSILON = 1e-8

def sanitize(value):
    if value is None:
        return None
    if isinstance(value, float):
        if np.isnan(value) or np.isinf(value):
            return None
    return value

def compute_metrics(fund_id: int, db: Session) -> FundMetricsSnapshot:
    # ---------------- Load Fund ----------------
    fund = db.get(MutualFund, fund_id)
    if not fund:
        raise ValueError("Fund not found")

    # ---------------- Load Fund NAVs ----------------
    navs = (
        db.query(NavData)
        .filter(NavData.fund_id == fund_id)
        .order_by(NavData.nav_date)
        .all()
    )

    if len(navs) < MIN_NAV_POINTS:
        raise ValueError("Not enough fund NAV data")

    df = pd.DataFrame(
        [(n.nav_date, float(n.nav_value)) for n in navs],
        columns=["date", "nav"],
    ).set_index("date")

    df["returns"] = df["nav"].pct_change()
    df = df.dropna()

    fund_ret = df["returns"]

    # ---------------- Load Benchmark NAVs ----------------
    benchmark_navs = (
        db.query(BenchmarkNav)
        .filter(BenchmarkNav.benchmark_name == fund.benchmark)
        .order_by(BenchmarkNav.nav_date)
        .all()
    )

    benchmark_available = len(benchmark_navs) >= MIN_NAV_POINTS

    if benchmark_available:
        bdf = pd.DataFrame(
            [(b.nav_date, float(b.nav_value)) for b in benchmark_navs],
            columns=["date", "nav"],
        ).set_index("date")

        bdf["returns"] = bdf["nav"].pct_change()
        bdf = bdf.dropna()

        aligned = df.join(bdf["returns"], how="inner", rsuffix="_bm").dropna()
        fund_ret = aligned["returns"]
        bm_ret = aligned["returns_bm"]
    else:
        bm_ret = None

    # ---------------- Risk-free rate (daily) ----------------
    rf_daily = RISK_FREE_RATE_ANNUAL / TRADING_DAYS

    # ---------------- Absolute Metrics ----------------
    std_deviation = None
    if len(fund_ret) > 1:
        std_val = np.std(fund_ret)
        if not np.isnan(std_val) and not np.isinf(std_val):
            std_deviation = std_val * np.sqrt(TRADING_DAYS)

    sharpe_ratio = None
    if fund.category.lower() == "Equity":
        std = np.std(fund_ret)
        if not np.isnan(std) and std > EPSILON:
            mean_ret = np.mean(fund_ret)
            if not np.isnan(mean_ret):
                sharpe_ratio = (mean_ret - rf_daily) / std
        else:
            sharpe_ratio = None

    downside = fund_ret[fund_ret < 0]
    sortino_ratio = None
    if fund.category.lower() == "Equity" and len(downside) > 0:
        downside_std = np.std(downside)
        mean_ret = np.mean(fund_ret)
        if (not np.isnan(downside_std) and not np.isnan(mean_ret) and 
            downside_std > EPSILON):
            sortino_ratio = ((mean_ret - rf_daily) * TRADING_DAYS) / (
                downside_std * np.sqrt(TRADING_DAYS)
            )
        else:
            sortino_ratio = None
    # ---------------- Benchmark-relative Metrics ----------------
    beta = None
    alpha = None
    r_squared = None
    upside_capture = None
    downside_capture = None

    if benchmark_available and bm_ret is not None and len(bm_ret) > 0:
        bm_var = np.var(bm_ret)
        if not np.isnan(bm_var) and bm_var != 0:
            cov_val = np.cov(fund_ret, bm_ret)
            if not np.isnan(cov_val[0][1]):
                beta = cov_val[0][1] / bm_var

        if beta is not None and not np.isnan(beta):
            mean_fund = np.mean(fund_ret)
            mean_bm = np.mean(bm_ret)
            if not np.isnan(mean_fund) and not np.isnan(mean_bm):
                alpha = (
                    (mean_fund * TRADING_DAYS)
                    - beta * (mean_bm * TRADING_DAYS)
                )
                if np.isnan(alpha):
                    alpha = None

                corr = np.corrcoef(fund_ret, bm_ret)[0, 1]
                if not np.isnan(corr):
                    r_squared = corr ** 2
                else:
                    r_squared = None

        up_mask = bm_ret > 0
        if up_mask.any():
            denom = bm_ret[up_mask].mean()
            if not np.isnan(denom) and abs(denom) > EPSILON:
                num = fund_ret[up_mask].mean()
                if not np.isnan(num):
                    upside_capture = num / denom

        down_mask = bm_ret < 0
        if down_mask.any():
            denom = bm_ret[down_mask].mean()
            if not np.isnan(denom) and abs(denom) > EPSILON:
                num = fund_ret[down_mask].mean()
                if not np.isnan(num):
                    downside_capture = num / denom
    # ---------------- Rolling Returns ----------------
    rolling_return_1y = None
    if len(fund_ret) >= TRADING_DAYS:
        rolling_return_1y = fund_ret[-TRADING_DAYS:].add(1).prod() - 1

    rolling_return_3y = None
    if len(fund_ret) >= TRADING_DAYS * 3:
        rolling_return_3y = fund_ret[-TRADING_DAYS * 3 :].add(1).prod() - 1

    # ---------------- Persist Snapshot ----------------
    return {
        "as_of_date": fund_ret.index.max(),
        "std_deviation": sanitize(std_deviation),
        "sharpe_ratio": sanitize(sharpe_ratio),
        "sortino_ratio": sanitize(sortino_ratio),
        "beta": sanitize(beta),
        "alpha": sanitize(alpha),
        "r_squared": sanitize(r_squared),
        "upside_capture": sanitize(upside_capture),
        "downside_capture": sanitize(downside_capture),
        "rolling_return_1y": sanitize(rolling_return_1y),
        "rolling_return_3y": sanitize(rolling_return_3y),
    }
