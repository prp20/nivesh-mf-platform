from typing import List, Optional
import csv
import io
from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from .. import crud, schemas

router = APIRouter(prefix="/benchmark-navs", tags=["benchmark-navs"])


# ============================================================================
# BENCHMARK NAV HISTORY ENDPOINTS
# ============================================================================

@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def create_benchmark_nav_bulk(
    bulk_nav: schemas.BenchmarkNavHistoryBulkCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create multiple benchmark NAV records from dictionary format.
    Expected format: {"benchmark_code": "NIFTY50", "nav_data": {"26-10-2021": 81.084, "25-10-2021": 79.604, ...}}
    Dates should be in YYYY-MM-DD format.
    """
    # Verify benchmark exists
    benchmark = await crud.get_benchmark_master(session, bulk_nav.benchmark_code)
    if not benchmark:
        raise HTTPException(status_code=404, detail=f"Benchmark {bulk_nav.benchmark_code} not found")
    
    try:
        inserted_count = await crud.bulk_insert_benchmark_nav_from_dict(session, bulk_nav.benchmark_code, bulk_nav.nav_data)
        return {
            "benchmark_code": bulk_nav.benchmark_code,
            "inserted": inserted_count,
            "message": f"Successfully inserted {inserted_count} benchmark NAV records for {bulk_nav.benchmark_code}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")


@router.put("/bulk/{benchmark_code}", status_code=status.HTTP_200_OK)
async def update_benchmark_nav_bulk(
    benchmark_code: str,
    bulk_nav: schemas.BenchmarkNavHistoryBulkUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update or append benchmark NAV records from dictionary format.
    Allows adding new dates or updating index values for existing dates.
    Expected format: {"nav_data": {"2021-10-26": 81.084, "2021-10-25": 79.604, ...}}
    Dates should be in YYYY-MM-DD format.
    """
    # Verify benchmark exists
    benchmark = await crud.get_benchmark_master(session, benchmark_code)
    if not benchmark:
        raise HTTPException(status_code=404, detail=f"Benchmark {benchmark_code} not found")
    
    try:
        inserted_count = await crud.bulk_insert_benchmark_nav_from_dict(session, benchmark_code, bulk_nav.nav_data)
        return {
            "benchmark_code": benchmark_code,
            "inserted": inserted_count,
            "message": f"Successfully inserted/updated {inserted_count} benchmark NAV records for {benchmark_code}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")


@router.patch("/bulk/{benchmark_code}", status_code=status.HTTP_200_OK)
async def patch_benchmark_nav_bulk(
    benchmark_code: str,
    bulk_nav: schemas.BenchmarkNavHistoryBulkUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Patch (partially update) benchmark NAV records from dictionary format.
    Same behavior as PUT - allows adding new dates or updating index values for existing dates.
    Expected format: {"nav_data": {"2021-10-26": 81.084, "2021-10-25": 79.604, ...}}
    Dates should be in YYYY-MM-DD format.
    """
    # Verify benchmark exists
    benchmark = await crud.get_benchmark_master(session, benchmark_code)
    if not benchmark:
        raise HTTPException(status_code=404, detail=f"Benchmark {benchmark_code} not found")
    
    try:
        inserted_count = await crud.bulk_insert_benchmark_nav_from_dict(session, benchmark_code, bulk_nav.nav_data)
        return {
            "benchmark_code": benchmark_code,
            "inserted": inserted_count,
            "message": f"Successfully inserted/updated {inserted_count} benchmark NAV records for {benchmark_code}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")


@router.post("/", response_model=schemas.BenchmarkNavHistoryRead, status_code=status.HTTP_201_CREATED)
async def create_benchmark_nav(
    nav: schemas.BenchmarkNavHistoryCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new benchmark NAV history record"""
    # Verify benchmark exists
    benchmark = await crud.get_benchmark_master(session, nav.benchmark_code)
    if not benchmark:
        raise HTTPException(status_code=404, detail=f"Benchmark {nav.benchmark_code} not found")
    
    return await crud.create_benchmark_nav_history(session, nav)


@router.get("/{benchmark_code}", response_model=List[schemas.BenchmarkNavHistoryRead])
async def get_benchmark_navs(
    benchmark_code: str,
    start_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session)
):
    """Get NAV history for a benchmark, optionally filtered by date range"""
    # Verify benchmark exists
    benchmark = await crud.get_benchmark_master(session, benchmark_code)
    if not benchmark:
        raise HTTPException(status_code=404, detail=f"Benchmark {benchmark_code} not found")
    
    if start_date and end_date:
        return await crud.get_benchmark_nav_by_date_range(session, benchmark_code, start_date, end_date)
    else:
        return await crud.get_benchmark_nav_history(session, benchmark_code)


@router.get("/{benchmark_code}/{nav_date}", response_model=schemas.BenchmarkNavHistoryRead)
async def get_benchmark_nav_by_date(
    benchmark_code: str,
    nav_date: str,
    session: AsyncSession = Depends(get_session)
):
    """Get NAV for a specific benchmark on a specific date"""
    navs = await crud.get_benchmark_nav_history(session, benchmark_code, nav_date)
    if not navs:
        raise HTTPException(status_code=404, detail=f"No NAV found for {benchmark_code} on {nav_date}")
    
    return navs[0]


@router.post("/bulk-csv", status_code=status.HTTP_202_ACCEPTED)
async def upload_benchmark_nav_csv(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Upload benchmark NAV data from CSV file.
    Expected columns: benchmark_code, nav_date, index_value
    """
    text_data = await file.read()
    s = text_data.decode()
    reader = csv.DictReader(io.StringIO(s))
    rows = []
    for r in reader:
        try:
            # Parse nav_date string to date object
            nav_date_obj = date_type.fromisoformat(r["nav_date"])
            r_parsed = {
                "benchmark_code": r["benchmark_code"],
                "nav_date": nav_date_obj,
                "index_value": float(r["index_value"]),
            }
            rows.append(r_parsed)
        except (ValueError, KeyError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
    
    await crud.bulk_insert_benchmark_nav_history(session, rows)
    return {"inserted": len(rows), "message": f"Successfully inserted {len(rows)} benchmark NAV records"}


@router.delete("/{benchmark_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_benchmark_nav_history(
    benchmark_code: str,
    nav_date: str | None = Query(None, description="Optional specific date to delete (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session)
):
    """Delete NAV history for a benchmark (all records or specific date)"""
    # Verify benchmark exists
    benchmark = await crud.get_benchmark_master(session, benchmark_code)
    if not benchmark:
        raise HTTPException(status_code=404, detail=f"Benchmark {benchmark_code} not found")
    
    await crud.delete_benchmark_nav_history(session, benchmark_code, nav_date)
    return None
