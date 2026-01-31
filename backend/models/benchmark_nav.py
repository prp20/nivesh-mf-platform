from sqlalchemy import Column, Integer, String, Date, Numeric, UniqueConstraint, Index
from .base import TimeSeriesBase


class BenchmarkNav(TimeSeriesBase):
    """Time-series data stored in TimescaleDB"""
    __tablename__ = "benchmark_nav"

    id = Column(Integer, primary_key=True)
    benchmark_name = Column(String(100), nullable=False)
    nav_date = Column(Date, nullable=False)
    nav_value = Column(Numeric(12, 6), nullable=False)

    __table_args__ = (
        UniqueConstraint("benchmark_name", "nav_date", name="uq_benchmark_date"),
        Index("ix_benchmark_date", "benchmark_name", "nav_date"),
    )
