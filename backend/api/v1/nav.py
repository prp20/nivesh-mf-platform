from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.session import get_db
from analytics.nav_ingestion import (
    ingest_nav_for_all_funds,
    ingest_nav_for_fund,
)
from backend.models.mutual_fund import MutualFund
from backend.models.nav_data import NavData

router = APIRouter()


@router.post("/nav/fetch/daily")
def fetch_daily_nav(db: Session = Depends(get_db)):
    """
    Fetches latest available NAVs for all funds from MFAPI.
    """
    result = ingest_nav_for_all_funds(db)
    return {
        "status": "completed",
        "details": result,
    }


@router.post("/nav/fetch/historical/{fund_id}")
def fetch_historical_nav(fund_id: int, db: Session = Depends(get_db)):
    fund = db.get(MutualFund, fund_id)
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")

    count = ingest_nav_for_fund(fund, db)
    return {
        "fund": fund.fund_name,
        "records_inserted": count,
    }


@router.get("/nav/{fund_id}")
def get_nav_history(fund_id: int, db: Session = Depends(get_db)):
    return (
        db.query(NavData)
        .filter(NavData.fund_id == fund_id)
        .order_by(NavData.nav_date)
        .all()
    )
