from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.fund_metrics_snapshot import FundMetricsSnapshot
from backend.models.mutual_fund import MutualFund

router = APIRouter()


@router.get("/compare")
def compare_funds(
    fund_ids: list[int] = Query(...),
    db: Session = Depends(get_db),
):
    results = []

    for fund_id in fund_ids:
        fund = db.get(MutualFund, fund_id)
        metrics = (
            db.query(FundMetricsSnapshot)
            .filter(FundMetricsSnapshot.fund_id == fund_id)
            .order_by(FundMetricsSnapshot.as_of_date.desc())
            .first()
        )
        if fund and metrics:
            results.append(
                {
                    "fund_id": fund.id,
                    "fund_name": fund.fund_name,
                    "category": fund.category,
                    "metrics": metrics,
                }
            )

    return {
        "count": len(results),
        "funds": results,
    }
