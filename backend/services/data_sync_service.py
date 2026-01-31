"""
Data synchronization service for mutual fund data ingestion.

This service handles the orchestration of data synchronization from
external sources like MFAPI, AMFI, and other data providers.
"""
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import insert, update
from backend.models.nav_data import NavData
from backend.models.mutual_fund import MutualFund
from analytics.nav_providers.mfapi import MFAPIProvider


class SyncJobTracker:
    """In-memory job tracker for sync operations."""
    
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
    
    def create_job(self, job_type: str) -> str:
        """Create a new sync job and return its ID."""
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "id": job_id,
            "type": job_type,
            "status": "running",
            "progress": 0,
            "message": "Initializing synchronization...",
            "created_at": datetime.utcnow(),
            "started_at": datetime.utcnow()
        }
        return job_id
    
    def update_job(self, job_id: str, progress: int, message: str):
        """Update job progress and message."""
        if job_id in self.jobs:
            self.jobs[job_id]["progress"] = min(progress, 100)
            self.jobs[job_id]["message"] = message
    
    def complete_job(self, job_id: str, status: str = "completed"):
        """Mark a job as complete."""
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status
            self.jobs[job_id]["progress"] = 100
            self.jobs[job_id]["completed_at"] = datetime.utcnow()
    
    def get_job_status(self, job_id: str) -> Dict[str, Any] | None:
        """Retrieve job status."""
        return self.jobs.get(job_id)


# Global job tracker instance
_job_tracker = SyncJobTracker()


class DataSyncService:
    """Service for synchronizing mutual fund data from external sources."""
    
    def __init__(self, db: Session):
        """Initialize the sync service with database session."""
        self.db = db
        self.mfapi_provider = MFAPIProvider()
    
    async def sync_nav_data_async(self) -> str:
        """
        Asynchronously synchronize NAV data from external sources.
        
        Returns:
            Job ID for tracking the sync operation.
        """
        job_id = _job_tracker.create_job("nav_data_sync")
        
        async def _sync():
            try:
                _job_tracker.update_job(job_id, 10, "Fetching funds list...")
                
                # Get list of funds
                funds = self.db.query(MutualFund).all()
                total_funds = len(funds)
                
                _job_tracker.update_job(job_id, 20, f"Found {total_funds} funds to sync")
                
                # Fetch NAV data for each fund
                synced_count = 0
                for idx, fund in enumerate(funds):
                    try:
                        nav_data = await self.mfapi_provider.get_nav_data(fund.isin)
                        
                        if nav_data:
                            # Store NAV data
                            for nav in nav_data:
                                db_nav = NavData(
                                    fund_id=fund.id,
                                    nav=nav.get("nav"),
                                    nav_date=nav.get("nav_date"),
                                    source="MFAPI"
                                )
                                self.db.add(db_nav)
                            synced_count += 1
                        
                        progress = 20 + int((idx / total_funds) * 70)
                        _job_tracker.update_job(
                            job_id,
                            progress,
                            f"Synced {synced_count}/{total_funds} funds"
                        )
                    except Exception as e:
                        print(f"Error syncing NAV for fund {fund.isin}: {str(e)}")
                        continue
                
                self.db.commit()
                _job_tracker.complete_job(job_id, "completed")
                _job_tracker.update_job(
                    job_id,
                    100,
                    f"Successfully synced NAV data for {synced_count} funds"
                )
            except Exception as e:
                _job_tracker.complete_job(job_id, "failed")
                _job_tracker.update_job(job_id, 0, f"Sync failed: {str(e)}")
                raise
        
        # Run async task in background
        asyncio.create_task(_sync())
        return job_id
    
    async def sync_funds_async(self) -> str:
        """
        Asynchronously synchronize fund metadata.
        
        Returns:
            Job ID for tracking the sync operation.
        """
        job_id = _job_tracker.create_job("funds_sync")
        
        async def _sync():
            try:
                _job_tracker.update_job(job_id, 10, "Fetching funds from MFAPI...")
                
                # Fetch funds from external source
                funds_data = await self.mfapi_provider.get_all_funds()
                
                _job_tracker.update_job(
                    job_id,
                    50,
                    f"Fetched {len(funds_data)} funds, updating database..."
                )
                
                # Update or insert funds
                for idx, fund_data in enumerate(funds_data):
                    existing_fund = self.db.query(MutualFund).filter(
                        MutualFund.isin == fund_data.get("isin")
                    ).first()
                    
                    if existing_fund:
                        # Update existing fund
                        for key, value in fund_data.items():
                            if hasattr(existing_fund, key):
                                setattr(existing_fund, key, value)
                    else:
                        # Create new fund
                        new_fund = MutualFund(**fund_data)
                        self.db.add(new_fund)
                    
                    progress = 50 + int((idx / len(funds_data)) * 45)
                    _job_tracker.update_job(
                        job_id,
                        progress,
                        f"Processing fund {idx + 1}/{len(funds_data)}"
                    )
                
                self.db.commit()
                _job_tracker.complete_job(job_id, "completed")
                _job_tracker.update_job(
                    job_id,
                    100,
                    f"Successfully synced {len(funds_data)} funds"
                )
            except Exception as e:
                _job_tracker.complete_job(job_id, "failed")
                _job_tracker.update_job(job_id, 0, f"Sync failed: {str(e)}")
                raise
        
        # Run async task in background
        asyncio.create_task(_sync())
        return job_id
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get the status of a sync job."""
        status = _job_tracker.get_job_status(job_id)
        
        if not status:
            return {
                "status": "not_found",
                "progress": 0,
                "message": f"Job {job_id} not found"
            }
        
        return {
            "status": status["status"],
            "progress": status["progress"],
            "message": status["message"]
        }
