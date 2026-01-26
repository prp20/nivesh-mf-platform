from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from backend.db.session import get_db
from backend.models.metrics_jobs import MetricsJob
from backend.models.mutual_fund import MutualFund
from backend.services.metrics_job_runner import run_metrics_job

router = APIRouter(prefix="/metrics/jobs", tags=["Metrics Jobs"])

@router.post("/{fund_id}")
def start_metrics_job(
    fund_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    fund = db.get(MutualFund, fund_id)
    if not fund:
        raise HTTPException(404, "Fund not found")

    active = (
        db.query(MetricsJob)
        .filter(
            MetricsJob.fund_id == fund_id,
            MetricsJob.status.in_(["PENDING", "RUNNING"]),
        )
        .first()
    )
    if active:
        raise HTTPException(409, "Metrics job already running")

    job = MetricsJob(fund_id=fund_id, status="PENDING")
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(run_metrics_job, job.id, fund_id, db)

    return {
        "job_id": job.id,
        "fund_id": fund_id,
        "status": job.status,
    }

@router.get("/{job_id}")
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    job = db.get(MetricsJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    return {
        "job_id": job.id,
        "fund_id": job.fund_id,
        "status": job.status,
        "error_message": job.error_message,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
    }