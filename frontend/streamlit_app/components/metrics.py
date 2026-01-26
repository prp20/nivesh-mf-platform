def safe_metric(metrics: dict, key: str, decimals: int = 2):
    value = metrics.get(key)
    if value is None:
        return "N/A"
    try:
        return round(float(value), decimals)
    except Exception:
        return "N/A"
    
def fund_health_score(metrics: dict) -> tuple[str, str]:
    """
    Returns (label, color)
    """
    score = 0

    if metrics.get("sharpe_ratio", 0) and metrics["sharpe_ratio"] > 1:
        score += 1
    if metrics.get("sortino_ratio", 0) and metrics["sortino_ratio"] > 1:
        score += 1
    if metrics.get("alpha", 0) and metrics["alpha"] > 0:
        score += 1
    if metrics.get("beta", 1) and metrics["beta"] < 1:
        score += 1
    if metrics.get("std_deviation", 999) and metrics["std_deviation"] < 20:
        score += 1

    if score >= 4:
        return "🟢 Strong", "green"
    elif score >= 2:
        return "🟡 Moderate", "orange"
    else:
        return "🔴 Weak", "red"