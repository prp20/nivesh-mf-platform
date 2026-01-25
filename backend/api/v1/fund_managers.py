from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.fund_manager import FundManager
from backend.api.schemas.fund_managers import (
    FundManagerCreate,
    FundManagerUpdate,
    FundManagerResponse,
)

router = APIRouter()


@router.post("/", response_model=FundManagerResponse, status_code=status.HTTP_201_CREATED)
def create_manager(payload: FundManagerCreate, db: Session = Depends(get_db)):
    manager = FundManager(**payload.model_dump())
    db.add(manager)
    db.commit()
    db.refresh(manager)
    return manager


@router.get("/", response_model=list[FundManagerResponse])
def list_managers(db: Session = Depends(get_db)):
    return db.query(FundManager).all()


@router.get("/{manager_id}", response_model=FundManagerResponse)
def get_manager(manager_id: int, db: Session = Depends(get_db)):
    manager = db.get(FundManager, manager_id)
    if not manager:
        raise HTTPException(status_code=404, detail="Fund manager not found")
    return manager


@router.put("/{manager_id}", response_model=FundManagerResponse)
def update_manager(
    manager_id: int,
    payload: FundManagerUpdate,
    db: Session = Depends(get_db),
):
    manager = db.get(FundManager, manager_id)
    if not manager:
        raise HTTPException(status_code=404, detail="Fund manager not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(manager, key, value)

    db.commit()
    db.refresh(manager)
    return manager


@router.delete("/{manager_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_manager(manager_id: int, db: Session = Depends(get_db)):
    manager = db.get(FundManager, manager_id)
    if not manager:
        raise HTTPException(status_code=404, detail="Fund manager not found")

    db.delete(manager)
    db.commit()
