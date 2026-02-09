from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from .. import crud, schemas

router = APIRouter(prefix="/funds", tags=["funds"])


@router.post("/", response_model=schemas.FundRead, status_code=status.HTTP_201_CREATED)
async def create_fund(fund: schemas.FundCreate, session: AsyncSession = Depends(get_session)):
    existing = await crud.get_fund_by_code(session, fund.scheme_code)
    if existing:
        raise HTTPException(status_code=400, detail="Fund exists")
    row = await crud.create_fund(session, fund)
    return row[0]


@router.get("/", response_model=List[schemas.FundRead])
async def list_funds(session: AsyncSession = Depends(get_session)):
    rows = await crud.get_all_funds(session)
    return rows


@router.get("/{scheme_code}", response_model=schemas.FundRead)
async def read_fund(scheme_code: str, session: AsyncSession = Depends(get_session)):
    fund = await crud.get_fund_by_code(session, scheme_code)
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    return fund


@router.put("/{scheme_code}", response_model=schemas.FundRead)
async def update_fund(scheme_code: str, fund_in: schemas.FundCreate, session: AsyncSession = Depends(get_session)):
    existing = await crud.get_fund_by_code(session, scheme_code)
    if not existing:
        raise HTTPException(status_code=404, detail="Fund not found")
    res = await crud.update_fund_by_code(session, scheme_code, fund_in)
    if not res:
        raise HTTPException(status_code=500, detail="Update failed")
    return res[0]


@router.delete("/{scheme_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fund(scheme_code: str, session: AsyncSession = Depends(get_session)):
    existing = await crud.get_fund_by_code(session, scheme_code)
    if not existing:
        raise HTTPException(status_code=404, detail="Fund not found")
    await crud.delete_fund_by_code(session, scheme_code)
    return None
