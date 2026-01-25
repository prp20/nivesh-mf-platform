from sqlalchemy import (
    Column,
    Integer,
    Date,
    Numeric,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .base import Base


class FundMetricsSnapshot(Base):
    __tablename__ = "fund_metrics_snapshot"

    id = Column(Integer, primary_key=True)

    fund_id = Column(
        Integer,
        ForeignKey("mutual_funds.id", ondelete="CASCADE"),
        nullable=False,
    )

    as_of_date = Column(Date, nullable=False)

    # Risk & Volatility
    std_deviation = Column(Numeric(10, 4), nullable=True)
    beta = Column(Numeric(10, 4), nullable=True)

    # Risk-adjusted metrics (Equity only)
    sharpe_ratio = Column(Numeric(10, 4), nullable=True)
    sortino_ratio = Column(Numeric(10, 4), nullable=True)

    # Regression metrics
    alpha = Column(Numeric(10, 4), nullable=True)
    r_squared = Column(Numeric(10, 4), nullable=True)

    # Market-cycle metrics
    upside_capture = Column(Numeric(10, 4), nullable=True)
    downside_capture = Column(Numeric(10, 4), nullable=True)

    # Rolling performance
    rolling_return_1y = Column(Numeric(10, 4), nullable=True)
    rolling_return_3y = Column(Numeric(10, 4), nullable=True)

    fund = relationship("MutualFund", back_populates="metrics")
