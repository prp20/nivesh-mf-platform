from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List
from ..database import get_session
from .. import schemas, crud, utils
import csv, io
from datetime import date as date_type

router = APIRouter(prefix="/navs", tags=["navs"])


# ============================================================================
# FUND NAV HISTORY ENDPOINTS
# ============================================================================

@router.post("/", response_model=schemas.FundNavHistoryRead, status_code=status.HTTP_201_CREATED)
async def create_fund_nav(
    nav: schemas.FundNavHistoryCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new NAV history record for a fund"""
    # Verify fund exists
    fund = await crud.get_fund_master_by_code(session, nav.scheme_code)
    if not fund:
        raise HTTPException(status_code=404, detail=f"Fund with scheme_code {nav.scheme_code} not found")
    return await crud.create_fund_nav_history(session, nav)


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def create_fund_nav_bulk(
    bulk_nav: schemas.FundNavHistoryBulkCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create multiple NAV records from dictionary format.
    Expected format: {"scheme_code": "MF001-D", "nav_data": {"26-10-2021": 81.084, "25-10-2021": 79.604, ...}}
    Dates should be in DD-MM-YYYY format.
    """
    # Verify fund exists
    fund = await crud.get_fund_master_by_code(session, bulk_nav.scheme_code)
    if not fund:
        raise HTTPException(status_code=404, detail=f"Fund with scheme_code {bulk_nav.scheme_code} not found")
    
    try:
        inserted_count = await crud.bulk_insert_fund_nav_from_dict(session, bulk_nav.scheme_code, bulk_nav.nav_data)
        return {
            "scheme_code": bulk_nav.scheme_code,
            "inserted": inserted_count,
            "message": f"Successfully inserted {inserted_count} NAV records for {bulk_nav.scheme_code}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")


@router.get("/{scheme_code}", response_model=List[schemas.FundNavHistoryRead])
async def get_fund_navs(
    scheme_code: str,
    start_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session)
):
    """Get NAV history for a fund, optionally filtered by date range"""
    # Verify fund exists
    fund = await crud.get_fund_master_by_code(session, scheme_code)
    if not fund:
        raise HTTPException(status_code=404, detail=f"Fund with scheme_code {scheme_code} not found")
    
    if start_date and end_date:
        return await crud.get_fund_nav_by_date_range(session, scheme_code, start_date, end_date)
    else:
        return await crud.get_fund_nav_history(session, scheme_code)


@router.get("/{scheme_code}/{nav_date}", response_model=schemas.FundNavHistoryRead)
async def get_fund_nav_by_date(
    scheme_code: str,
    nav_date: str,
    session: AsyncSession = Depends(get_session)
):
    """Get NAV for a specific fund on a specific date"""
    navs = await crud.get_fund_nav_history(session, scheme_code, nav_date)
    if not navs:
        raise HTTPException(status_code=404, detail=f"No NAV found for {scheme_code} on {nav_date}")
    return navs[0]


@router.post("/bulk-csv", status_code=status.HTTP_202_ACCEPTED)
async def upload_nav_csv(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Upload NAV data from CSV file.
    Expected columns: scheme_code, nav_date, nav_value
    """
    text_data = await file.read()
    s = text_data.decode()
    reader = csv.DictReader(io.StringIO(s))
    rows = []
    for r in reader:
        try:
            # Parse nav_date string to date object
            nav_date_obj = date_type.fromisoformat(r.get("nav_date") or r.get("date"))
            r_parsed = {
                "scheme_code": r["scheme_code"],
                "nav_date": nav_date_obj,
                "nav_value": float(r.get("nav_value") or r.get("nav")),
            }
            rows.append(r_parsed)
        except (ValueError, KeyError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
    
    await crud.bulk_insert_fund_nav_history(session, rows)
    return {"inserted": len(rows), "message": f"Successfully inserted {len(rows)} NAV records"}


@router.delete("/{scheme_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fund_nav_history(
    scheme_code: str,
    nav_date: str | None = Query(None, description="Optional specific date to delete (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session)
):
    """Delete NAV history for a fund (all records or specific date)"""
    # Verify fund exists
    fund = await crud.get_fund_master_by_code(session, scheme_code)
    if not fund:
        raise HTTPException(status_code=404, detail=f"Fund with scheme_code {scheme_code} not found")
    
    await crud.delete_fund_nav_history(session, scheme_code, nav_date)
    return None