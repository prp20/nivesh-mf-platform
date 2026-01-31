from sqlalchemy.orm import Session
from backend.models.fund_metrics_snapshot import FundMetricsSnapshot
from backend.models.mutual_fund import MutualFund


def compute_score(metrics, risk_profile: str) -> float:
    # Convert Decimal values to float to avoid type mixing errors
    def to_float(val):
        if val is None:
            return 0.0
        return float(val)
    
    score = 0.0

    # Positive contributors
    score += to_float(metrics.alpha) * 25
    score += to_float(metrics.sortino_ratio) * 20
    score += to_float(metrics.sharpe_ratio) * 15
    score += to_float(metrics.r_squared) * 10
    score += to_float(metrics.upside_capture) * 10

    # Negative contributors
    score -= abs(to_float(metrics.downside_capture)) * 10
    score -= to_float(metrics.std_deviation) * 5
    score -= abs(to_float(metrics.beta)) * 5

    # Risk profile bias
    if risk_profile == "low":
        score -= to_float(metrics.std_deviation) * 10
        score -= abs(to_float(metrics.beta)) * 10
    elif risk_profile == "high":
        score += to_float(metrics.alpha) * 10

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
                    "alpha": float(metrics.alpha) if metrics.alpha else None,
                    "sharpe": float(metrics.sharpe_ratio) if metrics.sharpe_ratio else None,
                    "sortino": float(metrics.sortino_ratio) if metrics.sortino_ratio else None,
                    "beta": float(metrics.beta) if metrics.beta else None,
                    "std_dev": float(metrics.std_deviation) if metrics.std_deviation else None,
                },
                "explanation": _explain(metrics, risk_profile),
            }
        )

    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations[:top_n]


def _explain(metrics, risk_profile: str) -> str:
    def to_float(val):
        if val is None:
            return 0.0
        return float(val)
    
    reasons = []

    if to_float(metrics.alpha) > 0:
        reasons.append("positive alpha indicates manager skill")

    if to_float(metrics.sortino_ratio) > 1:
        reasons.append("strong downside risk-adjusted returns")

    if to_float(metrics.beta) < 1 and to_float(metrics.beta) > 0:
        reasons.append("lower volatility than benchmark")

    if risk_profile == "low":
        reasons.append("aligned to low-risk preference")

    return ", ".join(reasons) or "balanced risk-return profile"
