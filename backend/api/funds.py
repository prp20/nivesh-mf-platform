from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.mutual_fund import MutualFund
from backend.api.schemas import MutualFundCreate, MutualFundResponse

router = APIRouter()


@router.post("/", response_model=MutualFundResponse)
def create_fund(payload: MutualFundCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(MutualFund)
        .filter(MutualFund.scheme_code == payload.scheme_code)
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Scheme code already exists")

    fund = MutualFund(**payload.dict())
    db.add(fund)
    db.commit()
    db.refresh(fund)
    return fund


@router.get("/", response_model=list[MutualFundResponse])
def list_funds(db: Session = Depends(get_db)):
    return db.query(MutualFund).all()
