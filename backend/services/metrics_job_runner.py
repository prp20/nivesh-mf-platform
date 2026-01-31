from datetime import datetime
from sqlalchemy.orm import Session

from analytics.metrics_engine import compute_metrics
from backend.models.metrics_jobs import MetricsJob
from backend.models.fund_metrics_snapshot import FundMetricsSnapshot

def run_metrics_job(job_id: int, fund_id: int, db: Session):
    job = db.get(MetricsJob, job_id)
    if not job:
        return

    try:
        job.status = "RUNNING"
        job.started_at = datetime.utcnow()
        db.commit()

        metrics = compute_metrics(fund_id, db)

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

        db.add(snapshot)

        job.status = "SUCCESS"
        job.finished_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        db.rollback()
        job.status = "FAILED"
        job.error_message = str(e)
        job.finished_at = datetime.utcnow()
        db.commit()
