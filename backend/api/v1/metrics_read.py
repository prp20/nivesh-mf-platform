from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import numpy as np
from fastapi.encoders import jsonable_encoder
import logging

from backend.db.session import get_db
from backend.models.fund_metrics_snapshot import FundMetricsSnapshot

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/metrics", tags=["Metrics"])


from decimal import Decimal

def sanitize(v):
    """Safely convert values to JSON-serializable format."""
    if v is None:
        return None

    # Decimal handling (CRITICAL)
    if isinstance(v, Decimal):
        if v.is_nan() or v.is_infinite():
            return None
        return float(v)

    if isinstance(v, (float, np.floating)):
        if np.isnan(v) or np.isinf(v):
            return None
        return float(v)

    return v

@router.get("/{fund_id}")
async def get_latest_metrics(fund_id: int, db: Session = Depends(get_db)):
    """
    Get the latest computed metrics for a fund.
    Returns 404 if no metrics have been computed yet.
    """
    snapshot = (
        db.query(FundMetricsSnapshot)
        .filter(FundMetricsSnapshot.fund_id == fund_id)
        .order_by(FundMetricsSnapshot.as_of_date.desc())
        .first()
    )

    if not snapshot:
        logger.info(f"No metrics found for fund {fund_id}")
        raise HTTPException(status_code=404, detail="Metrics not found")

    response = {
        "fund_id": snapshot.fund_id,
        "as_of_date": snapshot.as_of_date.isoformat(),
        "std_deviation": sanitize(snapshot.std_deviation),
        "sharpe_ratio": sanitize(snapshot.sharpe_ratio),
        "sortino_ratio": sanitize(snapshot.sortino_ratio),
        "beta": sanitize(snapshot.beta),
        "alpha": sanitize(snapshot.alpha),
        "r_squared": sanitize(snapshot.r_squared),
        "upside_capture": sanitize(snapshot.upside_capture),
        "downside_capture": sanitize(snapshot.downside_capture),
        "rolling_return_1y": sanitize(snapshot.rolling_return_1y),
        "rolling_return_3y": sanitize(snapshot.rolling_return_3y),
    }

    logger.debug(f"Retrieved metrics for fund {fund_id}: {response['as_of_date']}")
    return jsonable_encoder(response)
