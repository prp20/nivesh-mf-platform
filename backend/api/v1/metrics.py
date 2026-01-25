from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.fund_metrics_snapshot import FundMetricsSnapshot
from analytics.metrics_engine import compute_metrics

router = APIRouter()


@router.get("/metrics/{fund_id}")
def get_latest_metrics(fund_id: int, db: Session = Depends(get_db)):
    metrics = (
        db.query(FundMetricsSnapshot)
        .filter(FundMetricsSnapshot.fund_id == fund_id)
        .order_by(FundMetricsSnapshot.as_of_date.desc())
        .first()
    )
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")
    return metrics


@router.get("/metrics/{fund_id}/history")
def get_metrics_history(fund_id: int, db: Session = Depends(get_db)):
    return (
        db.query(FundMetricsSnapshot)
        .filter(FundMetricsSnapshot.fund_id == fund_id)
        .order_by(FundMetricsSnapshot.as_of_date.desc())
        .all()
    )


@router.post("/metrics/recompute/{fund_id}")
def recompute_metrics(fund_id: int, db: Session = Depends(get_db)):
    try:
        snapshot = compute_metrics(fund_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return snapshot


@router.delete("/metrics/{fund_id}")
def delete_metrics(fund_id: int, db: Session = Depends(get_db)):
    db.query(FundMetricsSnapshot).filter(
        FundMetricsSnapshot.fund_id == fund_id
    ).delete()
    db.commit()
    return {"message": "Metrics deleted"}
