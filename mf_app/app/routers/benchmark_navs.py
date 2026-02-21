from typing import List, Optional
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from .. import crud, schemas

router = APIRouter(prefix="/benchmark-navs", tags=["benchmark-navs"])


# ============================================================================
# BENCHMARK NAV HISTORY ENDPOINTS
# ============================================================================

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
        r_parsed = {
            "benchmark_code": r["benchmark_code"],
            "nav_date": r["nav_date"],
            "index_value": float(r["index_value"]),
        }
        rows.append(r_parsed)
    
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
