from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.nav_data import NavData
from backend.models.mutual_fund import MutualFund
from backend.api.schemas.nav import HistoricalNavRequest, NavResponse

router = APIRouter()


@router.post("/nav/fetch/daily")
def fetch_daily_nav(db: Session = Depends(get_db)):
    """
    Stub: later connect to AMFI / MFAPI.
    """
    funds = db.query(MutualFund).all()
    today = date.today()

    for fund in funds:
        exists = (
            db.query(NavData)
            .filter_by(fund_id=fund.id, nav_date=today)
            .first()
        )
        if not exists:
            nav = NavData(
                fund_id=fund.id,
                nav_date=today,
                nav_value=100.0,  # placeholder
            )
            db.add(nav)

    db.commit()
    return {"message": "Daily NAV fetch completed"}


@router.post("/nav/fetch/historical")
def fetch_historical_nav(
    payload: HistoricalNavRequest,
    db: Session = Depends(get_db),
):
    fund = db.get(MutualFund, payload.fund_id)
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")

    current = payload.start_date
    while current <= payload.end_date:
        exists = (
            db.query(NavData)
            .filter_by(fund_id=fund.id, nav_date=current)
            .first()
        )
        if not exists:
            db.add(
                NavData(
                    fund_id=fund.id,
                    nav_date=current,
                    nav_value=100.0,  # placeholder
                )
            )
        current = current.fromordinal(current.toordinal() + 1)

    db.commit()
    return {"message": "Historical NAV fetch completed"}


@router.get("/nav/{fund_id}", response_model=list[NavResponse])
def get_nav_history(fund_id: int, db: Session = Depends(get_db)):
    return (
        db.query(NavData)
        .filter(NavData.fund_id == fund_id)
        .order_by(NavData.nav_date)
        .all()
    )


@router.delete("/nav/{fund_id}")
def delete_nav_data(fund_id: int, db: Session = Depends(get_db)):
    db.query(NavData).filter(NavData.fund_id == fund_id).delete()
    db.commit()
    return {"message": "NAV data deleted"}
