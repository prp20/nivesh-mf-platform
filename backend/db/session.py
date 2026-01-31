import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings

# PostgreSQL engine for relational data
postgres_url = os.getenv("POSTGRES_URL", settings.postgres_url)
postgres_engine = create_engine(
    postgres_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
)

PostgresSessionLocal = sessionmaker(
    bind=postgres_engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

# TimescaleDB engine for time-series data
timescaledb_url = os.getenv("TIMESCALEDB_URL", settings.timescaledb_url)
timescaledb_engine = create_engine(
    timescaledb_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
)

TimeScaleDBSessionLocal = sessionmaker(
    bind=timescaledb_engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

# Backward compatibility - default is postgres
engine = postgres_engine
SessionLocal = PostgresSessionLocal

def get_db():
    """Get PostgreSQL session for relational data"""
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_timescaledb():
    """Get TimescaleDB session for time-series data"""
    db = TimeScaleDBSessionLocal()
    try:
        yield db
    finally:
        db.close()