from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from backend.db.session import get_db
from backend.models.metrics_jobs import MetricsJob
from backend.models.mutual_fund import MutualFund
from backend.services.metrics_job_runner import run_metrics_job, run_metrics_job_async

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics/jobs", tags=["Metrics Jobs"])

@router.post("/{fund_id}")
async def start_metrics_job(
    fund_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Start a metrics computation job for a fund.
    Returns existing job if one is already running.
    """
    fund = db.get(MutualFund, fund_id)
    if not fund:
        raise HTTPException(404, "Fund not found")

    active = (
        db.query(MetricsJob)
        .filter(
            MetricsJob.fund_id == fund_id,
            MetricsJob.status.in_(["PENDING", "RUNNING"]),
            MetricsJob.finished_at == None,  # Only consider jobs that haven't finished
        )
        .first()
    )
    if active:
        # Return existing job instead of error
        return {
            "job_id": active.id,
            "fund_id": active.fund_id,
            "status": active.status,
            "is_duplicate": True,
            "message": "Job already running for this fund",
        }

    job = MetricsJob(fund_id=fund_id, status="PENDING")
    db.add(job)
    db.commit()
    db.refresh(job)

    # Add async task to background (pass job_id and fund_id, NOT db)
    background_tasks.add_task(run_metrics_job, job.id, fund_id)

    logger.info(f"[ENDPOINT] Created metrics job {job.id} for fund {fund_id}, added to background tasks")
    
    return {
        "job_id": job.id,
        "fund_id": fund_id,
        "status": job.status,
        "is_duplicate": False,
    }

@router.get("/{job_id}")
async def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """Get the status of a metrics computation job."""
    job = db.get(MetricsJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    # Calculate progress percentage based on status
    progress_map = {
        "PENDING": 10,
        "RUNNING": 50,
        "SUCCESS": 100,
        "FAILED": 100,
    }
    progress = progress_map.get(job.status, 0)

    return {
        "job_id": job.id,
        "fund_id": job.fund_id,
        "status": job.status,
        "progress": progress,
        "error_message": job.error_message,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
    }