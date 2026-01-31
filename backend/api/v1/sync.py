"""
Data synchronization endpoints for the mutual fund analysis platform.

This module provides REST API endpoints for triggering and monitoring
data synchronization operations from external sources.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.services.data_sync_service import DataSyncService
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


class SyncResponse(BaseModel):
    """Response model for sync operations."""
    status: str
    message: str
    job_id: str | None = None


class SyncStatusResponse(BaseModel):
    """Response model for sync status checks."""
    status: str
    progress: int
    message: str


@router.post("/nav-data")
async def sync_nav_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> SyncResponse:
    """
    Trigger synchronization of NAV data from external sources.
    
    This endpoint queues a background job to sync NAV data from
    the configured providers and stores it in the database.
    """
    try:
        sync_service = DataSyncService(db)
        job_id = await sync_service.sync_nav_data_async()
        
        return SyncResponse(
            status="queued",
            message="NAV data synchronization started",
            job_id=job_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/funds")
async def sync_funds(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> SyncResponse:
    """
    Trigger synchronization of mutual fund metadata.
    
    This endpoint queues a background job to sync fund information
    from the configured sources.
    """
    try:
        sync_service = DataSyncService(db)
        job_id = await sync_service.sync_funds_async()
        
        return SyncResponse(
            status="queued",
            message="Funds synchronization started",
            job_id=job_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}")
async def get_sync_status(
    job_id: str,
    db: Session = Depends(get_db)
) -> SyncStatusResponse:
    """Get the status of a sync job."""
    try:
        sync_service = DataSyncService(db)
        status = await sync_service.get_job_status(job_id)
        
        return SyncStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
