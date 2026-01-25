import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from backend.models.nav_data import NavData
from backend.models.benchmark_nav import BenchmarkNav
from backend.models.fund_metrics_snapshot import FundMetricsSnapshot
from backend.models.mutual_fund import MutualFund


RISK_FREE_RATE = 0.05  # 5% annual (configurable later)


def compute_metrics(fund_id: int, db: Session) -> FundMetricsSnapshot:
    fund = db.get(MutualFund, fund_id)
    if not fund:
        raise ValueError("Fund not found")

    navs = (
        db.query(NavData)
        .filter(NavData.fund_id == fund_id)
        .order_by(NavData.nav_date)
        .all()
    )

    if len(navs) < 30:
        raise ValueError("Not enough NAV data")

    df = pd.DataFrame(
        [(n.nav_date, float(n.nav_value)) for n in navs],
        columns=["date", "nav"],
    ).set_index("date")

    df["returns"] = df["nav"].pct_change().dropna()

    # Benchmark
    benchmark_navs = (
        db.query(BenchmarkNav)
        .filter(BenchmarkNav.benchmark_name == fund.benchmark)
        .order_by(BenchmarkNav.nav_date)
        .all()
    )

    bdf = pd.DataFrame(
        [(b.nav_date, float(b.nav_value)) for b in benchmark_navs],
        columns=["date", "nav"],
    ).set_index("date")

    bdf["returns"] = bdf["nav"].pct_change().dropna()

    aligned = df.join(bdf["returns"], how="inner", rsuffix="_bm").dropna()

    fund_ret = aligned["returns"]
    bm_ret = aligned["returns_bm"]

    # Metrics
    std_dev = fund_ret.std() * np.sqrt(252)
    sharpe = ((fund_ret.mean() * 252) - RISK_FREE_RATE) / std_dev
    downside_std = fund_ret[fund_ret < 0].std() * np.sqrt(252)
    sortino = ((fund_ret.mean() * 252) - RISK_FREE_RATE) / downside_std

    beta = np.cov(fund_ret, bm_ret)[0][1] / np.var(bm_ret)
    alpha = (fund_ret.mean() * 252) - beta * (bm_ret.mean() * 252)
    r_squared = np.corrcoef(fund_ret, bm_ret)[0, 1] ** 2

    upside_capture = fund_ret[bm_ret > 0].mean() / bm_ret[bm_ret > 0].mean()
    downside_capture = fund_ret[bm_ret < 0].mean() / bm_ret[bm_ret < 0].mean()

    snapshot = FundMetricsSnapshot(
        fund_id=fund_id,
        as_of_date=aligned.index.max(),
        std_deviation=std_dev,
        sharpe_ratio=sharpe if fund.category.lower() == "equity" else None,
        sortino_ratio=sortino if fund.category.lower() == "equity" else None,
        beta=beta,
        alpha=alpha,
        r_squared=r_squared,
        upside_capture=upside_capture,
        downside_capture=downside_capture,
        rolling_return_1y=(fund_ret[-252:].add(1).prod() - 1),
        rolling_return_3y=(fund_ret[-756:].add(1).prod() - 1)
        if len(fund_ret) > 756
        else None,
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot
