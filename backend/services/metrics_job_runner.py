from datetime import datetime
from sqlalchemy.orm import Session
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from analytics.metrics_engine import compute_metrics
from backend.models.metrics_jobs import MetricsJob
from backend.models.fund_metrics_snapshot import FundMetricsSnapshot
from backend.db.session import PostgresSessionLocal, TimeScaleDBSessionLocal

logger = logging.getLogger(__name__)

# Thread pool for blocking database operations
executor = ThreadPoolExecutor(max_workers=4)

def _run_metrics_job_sync(job_id: int, fund_id: int) -> dict:
    """
    Synchronous metrics computation function.
    This runs in a thread pool to avoid blocking the async event loop.
    """
    logger.info(f"[SYNC_TASK] Starting metrics computation: job_id={job_id}, fund_id={fund_id}")
    db_postgres = PostgresSessionLocal()
    db_timescale = TimeScaleDBSessionLocal()
    
    try:
        job = db_postgres.get(MetricsJob, job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return {"status": "error", "message": "Job not found"}

        # Mark job as running
        job.status = "RUNNING"
        job.started_at = datetime.utcnow()
        db_postgres.commit()

        # Compute metrics using correct database sessions
        metrics = compute_metrics(fund_id, db_postgres, db_timescale)

        # Create and persist metrics snapshot
        snapshot = FundMetricsSnapshot(
            fund_id=fund_id,
            as_of_date=metrics["as_of_date"],
            std_deviation=metrics["std_deviation"],
            sharpe_ratio=metrics["sharpe_ratio"],
            sortino_ratio=metrics["sortino_ratio"],
            beta=metrics["beta"],
            alpha=metrics["alpha"],
            r_squared=metrics["r_squared"],
            upside_capture=metrics["upside_capture"],
            downside_capture=metrics["downside_capture"],
            rolling_return_1y=metrics["rolling_return_1y"],
            rolling_return_3y=metrics["rolling_return_3y"],
        )

        db_postgres.add(snapshot)

        # Mark job as successful
        job.status = "SUCCESS"
        job.finished_at = datetime.utcnow()
        db_postgres.commit()
        logger.info(f"Job {job_id} completed successfully")
        return {"status": "success", "job_id": job_id}

    except Exception as e:
        logger.error(f"Job {job_id} failed with error: {str(e)}", exc_info=True)
        
        # Ensure we close the old connection before opening a new one
        try:
            db_postgres.rollback()
        except Exception as rb_error:
            logger.error(f"Rollback failed: {str(rb_error)}")
        
        # Create a fresh session to update job status
        try:
            db_postgres_retry = PostgresSessionLocal()
            job_retry = db_postgres_retry.get(MetricsJob, job_id)
            if job_retry:
                job_retry.status = "FAILED"
                job_retry.error_message = str(e)
                job_retry.finished_at = datetime.utcnow()
                db_postgres_retry.commit()
                logger.info(f"Job {job_id} marked as FAILED")
            db_postgres_retry.close()
        except Exception as retry_error:
            logger.error(f"Failed to update job status for {job_id}: {str(retry_error)}", exc_info=True)
        
        return {"status": "error", "job_id": job_id, "error": str(e)}
    
    finally:
        try:
            db_postgres.close()
            db_timescale.close()
        except Exception as close_error:
            logger.error(f"Error closing database connections: {str(close_error)}")


async def run_metrics_job_async(job_id: int, fund_id: int):
    """
    Async wrapper for metrics computation.
    Runs the synchronous computation in a thread pool to avoid blocking.
    """
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, _run_metrics_job_sync, job_id, fund_id)
    return result


# Backward compatibility - sync version for background tasks
def run_metrics_job(job_id: int, fund_id: int):
    """Synchronous entry point for background tasks (FastAPI BackgroundTasks)."""
    logger.info(f"Background task started: run_metrics_job({job_id}, {fund_id})")
    _run_metrics_job_sync(job_id, fund_id)
    logger.info(f"Background task completed: job_id={job_id}")
