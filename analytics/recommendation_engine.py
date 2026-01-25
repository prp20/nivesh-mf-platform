from sqlalchemy.orm import Session
from backend.models.fund_metrics_snapshot import FundMetricsSnapshot
from backend.models.mutual_fund import MutualFund


def compute_score(metrics, risk_profile: str) -> float:
    score = 0.0

    # Positive contributors
    score += (metrics.alpha or 0) * 25
    score += (metrics.sortino_ratio or 0) * 20
    score += (metrics.sharpe_ratio or 0) * 15
    score += (metrics.r_squared or 0) * 10
    score += (metrics.upside_capture or 0) * 10

    # Negative contributors
    score -= abs(metrics.downside_capture or 0) * 10
    score -= (metrics.std_deviation or 0) * 5
    score -= abs(metrics.beta or 0) * 5

    # Risk profile bias
    if risk_profile == "low":
        score -= (metrics.std_deviation or 0) * 10
        score -= abs(metrics.beta or 0) * 10
    elif risk_profile == "high":
        score += (metrics.alpha or 0) * 10

    return round(score, 4)


def recommend_funds(
    db: Session,
    risk_profile: str,
    category: str | None,
    top_n: int,
):
    query = (
        db.query(FundMetricsSnapshot, MutualFund)
        .join(MutualFund, MutualFund.id == FundMetricsSnapshot.fund_id)
    )

    if category:
        query = query.filter(MutualFund.category == category)

    rows = query.all()

    recommendations = []
    for metrics, fund in rows:
        score = compute_score(metrics, risk_profile)
        recommendations.append(
            {
                "fund_id": fund.id,
                "fund_name": fund.fund_name,
                "category": fund.category,
                "benchmark": fund.benchmark,
                "score": score,
                "key_metrics": {
                    "alpha": metrics.alpha,
                    "sharpe": metrics.sharpe_ratio,
                    "sortino": metrics.sortino_ratio,
                    "beta": metrics.beta,
                    "std_dev": metrics.std_deviation,
                },
                "explanation": _explain(metrics, risk_profile),
            }
        )

    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations[:top_n]


def _explain(metrics, risk_profile: str) -> str:
    reasons = []

    if metrics.alpha and metrics.alpha > 0:
        reasons.append("positive alpha indicates manager skill")

    if metrics.sortino_ratio and metrics.sortino_ratio > 1:
        reasons.append("strong downside risk-adjusted returns")

    if metrics.beta and metrics.beta < 1:
        reasons.append("lower volatility than benchmark")

    if risk_profile == "low":
        reasons.append("aligned to low-risk preference")

    return ", ".join(reasons) or "balanced risk-return profile"
