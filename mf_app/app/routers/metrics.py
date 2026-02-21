from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from .. import crud, schemas

router = APIRouter(prefix="/metrics", tags=["metrics"])


# ============================================================================
# FUND METRICS ENDPOINTS
# ============================================================================

@router.post("/", response_model=schemas.FundMetricsRead, status_code=status.HTTP_201_CREATED)
async def create_fund_metrics(
    metrics: schemas.FundMetricsCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create or update fund performance metrics"""
    # Verify fund exists
    fund = await crud.get_fund_master_by_code(session, metrics.scheme_code)
    if not fund:
        raise HTTPException(status_code=404, detail=f"Fund with scheme_code {metrics.scheme_code} not found")
    
    return await crud.create_fund_metrics(session, metrics)


@router.get("/", response_model=List[schemas.FundMetricsRead])
async def list_fund_metrics(session: AsyncSession = Depends(get_session)):
    """Get all fund metrics (latest records)"""
    return await crud.get_all_fund_metrics(session)


@router.get("/{scheme_code}", response_model=schemas.FundMetricsRead)
async def get_fund_metrics(
    scheme_code: str,
    session: AsyncSession = Depends(get_session)
):
    """Get metrics for a specific fund"""
    # Verify fund exists
    fund = await crud.get_fund_master_by_code(session, scheme_code)
    if not fund:
        raise HTTPException(status_code=404, detail=f"Fund with scheme_code {scheme_code} not found")
    
    metrics = await crud.get_fund_metrics(session, scheme_code)
    if not metrics:
        raise HTTPException(status_code=404, detail=f"Metrics not found for fund {scheme_code}")
    
    return metrics


@router.put("/{scheme_code}", response_model=schemas.FundMetricsRead)
async def update_fund_metrics(
    scheme_code: str,
    metrics_in: schemas.FundMetricsUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update fund metrics"""
    # Verify fund exists
    fund = await crud.get_fund_master_by_code(session, scheme_code)
    if not fund:
        raise HTTPException(status_code=404, detail=f"Fund with scheme_code {scheme_code} not found")
    
    existing = await crud.get_fund_metrics(session, scheme_code)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Metrics not found for fund {scheme_code}")
    
    result = await crud.update_fund_metrics(session, scheme_code, metrics_in)
    if not result:
        raise HTTPException(status_code=500, detail="Update failed")
    
    return result


@router.patch("/{scheme_code}", response_model=schemas.FundMetricsRead)
async def patch_fund_metrics(
    scheme_code: str,
    metrics_in: schemas.FundMetricsUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Partially update fund metrics"""
    # Verify fund exists
    fund = await crud.get_fund_master_by_code(session, scheme_code)
    if not fund:
        raise HTTPException(status_code=404, detail=f"Fund with scheme_code {scheme_code} not found")
    
    existing = await crud.get_fund_metrics(session, scheme_code)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Metrics not found for fund {scheme_code}")
    
    result = await crud.update_fund_metrics(session, scheme_code, metrics_in)
    if not result:
        raise HTTPException(status_code=500, detail="Update failed")
    
    return result


@router.delete("/{scheme_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fund_metrics(
    scheme_code: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete metrics for a fund"""
    # Verify fund exists
    fund = await crud.get_fund_master_by_code(session, scheme_code)
    if not fund:
        raise HTTPException(status_code=404, detail=f"Fund with scheme_code {scheme_code} not found")
    
    await crud.delete_fund_metrics(session, scheme_code)
    return None
