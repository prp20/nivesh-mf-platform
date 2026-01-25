from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.api.schemas.recommend import RecommendationRequest
from analytics.recommendation_engine import recommend_funds

router = APIRouter()


@router.post("/recommend")
def recommend(payload: RecommendationRequest, db: Session = Depends(get_db)):
    results = recommend_funds(
        db=db,
        risk_profile=payload.risk_profile,
        category=payload.category,
        top_n=payload.top_n,
    )

    return {
        "risk_profile": payload.risk_profile,
        "count": len(results),
        "recommendations": results,
        "disclaimer": (
            "Recommendations are for educational purposes only "
            "and do not constitute investment advice."
        ),
    }
