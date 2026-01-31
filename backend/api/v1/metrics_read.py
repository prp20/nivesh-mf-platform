from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import numpy as np
from fastapi.encoders import jsonable_encoder

from backend.db.session import get_db
from backend.models.fund_metrics_snapshot import FundMetricsSnapshot

router = APIRouter(prefix="/metrics", tags=["Metrics"])


from decimal import Decimal
import numpy as np

def sanitize(v):
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
        return v

    return v

@router.get("/{fund_id}")
def get_latest_metrics(fund_id: int, db: Session = Depends(get_db)):
    snapshot = (
        db.query(FundMetricsSnapshot)
        .filter(FundMetricsSnapshot.fund_id == fund_id)
        .order_by(FundMetricsSnapshot.as_of_date.desc())
        .first()
    )

    if not snapshot:
        raise HTTPException(status_code=404, detail="Metrics not available")

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

    return jsonable_encoder(response)
