from pydantic import BaseModel
from typing import Optional, Literal


class RecommendationRequest(BaseModel):
    risk_profile: Literal["low", "medium", "high"]
    investment_horizon_years: int
    category: Optional[str] = None  # Equity, Debt, Hybrid
    top_n: int = 5
