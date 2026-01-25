from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.mutual_fund import MutualFund
from backend.api.schemas.funds import (
    FundCreate,
    FundUpdate,
    FundResponse,
)

router = APIRouter()


@router.post("/", response_model=FundResponse, status_code=status.HTTP_201_CREATED)
def create_fund(payload: FundCreate, db: Session = Depends(get_db)):
    exists = (
        db.query(MutualFund)
        .filter(MutualFund.scheme_code == payload.scheme_code)
        .first()
    )
    if exists:
        raise HTTPException(
            status_code=400, detail="Fund with this scheme_code already exists"
        )

    fund = MutualFund(**payload.model_dump())
    db.add(fund)
    db.commit()
    db.refresh(fund)
    return fund


@router.get("/", response_model=list[FundResponse])
def list_funds(db: Session = Depends(get_db)):
    return db.query(MutualFund).all()


@router.get("/{fund_id}", response_model=FundResponse)
def get_fund(fund_id: int, db: Session = Depends(get_db)):
    fund = db.get(MutualFund, fund_id)
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    return fund


@router.put("/{fund_id}", response_model=FundResponse)
def update_fund(
    fund_id: int,
    payload: FundUpdate,
    db: Session = Depends(get_db),
):
    fund = db.get(MutualFund, fund_id)
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(fund, key, value)

    db.commit()
    db.refresh(fund)
    return fund


@router.delete("/{fund_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fund(fund_id: int, db: Session = Depends(get_db)):
    fund = db.get(MutualFund, fund_id)
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")

    db.delete(fund)
    db.commit()
