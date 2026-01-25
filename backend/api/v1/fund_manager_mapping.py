from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.mutual_fund import MutualFund
from backend.models.fund_manager import FundManager
from backend.models.fund_manager_mapping import FundManagerMapping

router = APIRouter()


@router.post(
    "/funds/{fund_id}/managers/{manager_id}",
    status_code=status.HTTP_201_CREATED,
)
def assign_manager_to_fund(
    fund_id: int,
    manager_id: int,
    db: Session = Depends(get_db),
):
    fund = db.get(MutualFund, fund_id)
    manager = db.get(FundManager, manager_id)

    if not fund or not manager:
        raise HTTPException(status_code=404, detail="Fund or Manager not found")

    exists = (
        db.query(FundManagerMapping)
        .filter_by(fund_id=fund_id, manager_id=manager_id)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Manager already assigned")

    mapping = FundManagerMapping(
        fund_id=fund_id,
        manager_id=manager_id,
    )
    db.add(mapping)
    db.commit()
    return {"message": "Manager assigned to fund"}


@router.delete(
    "/funds/{fund_id}/managers/{manager_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_manager_from_fund(
    fund_id: int,
    manager_id: int,
    db: Session = Depends(get_db),
):
    mapping = (
        db.query(FundManagerMapping)
        .filter_by(fund_id=fund_id, manager_id=manager_id)
        .first()
    )

    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")

    db.delete(mapping)
    db.commit()


@router.get("/funds/{fund_id}/managers")
def list_fund_managers(fund_id: int, db: Session = Depends(get_db)):
    fund = db.get(MutualFund, fund_id)
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")

    return fund.managers
