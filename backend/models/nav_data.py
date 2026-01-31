from sqlalchemy import (
    Column,
    Integer,
    Date,
    Numeric,
    Index,
    UniqueConstraint,
)

from .base import TimeSeriesBase


class NavData(TimeSeriesBase):
    """Time-series data stored in TimescaleDB"""
    __tablename__ = "nav_data"

    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, nullable=False)  # FK to PostgreSQL mutual_funds.id
    nav_date = Column(Date, nullable=False)
    nav_value = Column(Numeric(12, 6), nullable=False)

    __table_args__ = (
        UniqueConstraint("fund_id", "nav_date", name="uq_fund_nav_date"),
        Index("ix_nav_fund_date", "fund_id", "nav_date"),
    )

