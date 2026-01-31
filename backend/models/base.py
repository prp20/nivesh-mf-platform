from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base model for PostgreSQL relational data"""
    pass


class TimeSeriesBase(DeclarativeBase):
    """Base model for TimescaleDB time-series data"""
    pass
