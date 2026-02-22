from sqlalchemy import select, insert, text, update, delete, cast, Date
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql import literal
from .models import (
    FundMaster, FundMetrics, FundNavHistory, 
    BenchmarkMaster, BenchmarkNavHistory
)
from .schemas import (
    FundMasterCreate, FundMasterUpdate,
    FundMetricsCreate, FundMetricsUpdate,
    FundNavHistoryCreate,
    BenchmarkMasterCreate, BenchmarkMasterUpdate,
    BenchmarkNavHistoryCreate
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date as date_type
from datetime import datetime

# ============================================================================
# FUND MASTER CRUD OPERATIONS
# ============================================================================

async def create_fund_master(session: AsyncSession, fund_in: FundMasterCreate):
    stmt = insert(FundMaster).values(**fund_in.model_dump()).returning(FundMaster)
    res = await session.execute(stmt)
    await session.commit()
    return res.scalar_one()


async def get_fund_master_by_code(session: AsyncSession, scheme_code: str):
    q = select(FundMaster).where(FundMaster.scheme_code == scheme_code)
    res = await session.execute(q)
    return res.scalar_one_or_none()


async def get_all_fund_masters(session: AsyncSession, is_active: Optional[bool] = None):
    q = select(FundMaster)
    if is_active is not None:
        q = q.where(FundMaster.is_active == is_active)
    res = await session.execute(q)
    return res.scalars().all()


async def update_fund_master(session: AsyncSession, scheme_code: str, fund_in: FundMasterUpdate):
    data = fund_in.model_dump(exclude_unset=True)
    if not data:
        return await get_fund_master_by_code(session, scheme_code)
    stmt = (
        update(FundMaster)
        .where(FundMaster.scheme_code == scheme_code)
        .values(**data)
        .returning(FundMaster)
    )
    res = await session.execute(stmt)
    await session.commit()
    return res.scalar_one_or_none()


async def delete_fund_master(session: AsyncSession, scheme_code: str):
    stmt = delete(FundMaster).where(FundMaster.scheme_code == scheme_code).returning(FundMaster)
    res = await session.execute(stmt)
    await session.commit()
    return res.scalar_one_or_none()


# ============================================================================
# FUND METRICS CRUD OPERATIONS
# ============================================================================

async def create_fund_metrics(session: AsyncSession, metrics_in: FundMetricsCreate):
    stmt = insert(FundMetrics).values(**metrics_in.model_dump()).returning(FundMetrics)
    res = await session.execute(stmt)
    await session.commit()
    return res.scalar_one()


async def get_fund_metrics(session: AsyncSession, scheme_code: str):
    q = select(FundMetrics).where(FundMetrics.scheme_code == scheme_code)
    res = await session.execute(q)
    return res.scalar_one_or_none()


async def get_all_fund_metrics(session: AsyncSession):
    q = select(FundMetrics).order_by(FundMetrics.nav_date.desc())
    res = await session.execute(q)
    return res.scalars().all()


async def update_fund_metrics(session: AsyncSession, scheme_code: str, metrics_in: FundMetricsUpdate):
    data = metrics_in.model_dump(exclude_unset=True)
    if not data:
        return await get_fund_metrics(session, scheme_code)
    stmt = (
        update(FundMetrics)
        .where(FundMetrics.scheme_code == scheme_code)
        .values(**data)
        .returning(FundMetrics)
    )
    res = await session.execute(stmt)
    await session.commit()
    return res.scalar_one_or_none()


async def delete_fund_metrics(session: AsyncSession, scheme_code: str):
    stmt = delete(FundMetrics).where(FundMetrics.scheme_code == scheme_code).returning(FundMetrics)
    res = await session.execute(stmt)
    await session.commit()
    return res.scalar_one_or_none()


# ============================================================================
# FUND NAV HISTORY CRUD OPERATIONS
# ============================================================================

async def create_fund_nav_history(session: AsyncSession, nav_in: FundNavHistoryCreate):
    stmt = insert(FundNavHistory).values(**nav_in.model_dump()).returning(FundNavHistory)
    res = await session.execute(stmt)
    await session.commit()
    return res.scalar_one()


async def get_fund_nav_history(session: AsyncSession, scheme_code: str, nav_date: Optional[str] = None):
    q = select(FundNavHistory).where(FundNavHistory.scheme_code == scheme_code)
    if nav_date:
        # Convert string date to DATE type for proper comparison
        try:
            nav_date_obj = date_type.fromisoformat(nav_date)
            q = q.where(FundNavHistory.nav_date == nav_date_obj)
        except (ValueError, TypeError):
            # If date parsing fails, return empty list
            return []
    q = q.order_by(FundNavHistory.nav_date.desc())
    res = await session.execute(q)
    return res.scalars().all()


async def get_fund_nav_by_date_range(session: AsyncSession, scheme_code: str, start_date: str, end_date: str):
    try:
        start_date_obj = date_type.fromisoformat(start_date)
        end_date_obj = date_type.fromisoformat(end_date)
    except (ValueError, TypeError):
        # If date parsing fails, return empty list
        return []
    
    q = select(FundNavHistory).where(
        (FundNavHistory.scheme_code == scheme_code) &
        (FundNavHistory.nav_date >= start_date_obj) &
        (FundNavHistory.nav_date <= end_date_obj)
    ).order_by(FundNavHistory.nav_date.desc())
    res = await session.execute(q)
    return res.scalars().all()


async def bulk_insert_fund_nav_history(session: AsyncSession, rows: list[dict]):
    if not rows:
        return True
    # Use PostgreSQL ON CONFLICT for upsert
    stmt = pg_insert(FundNavHistory).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=['scheme_code', 'nav_date'],
        set_=dict(nav_value=stmt.excluded.nav_value)
    )
    await session.execute(stmt)
    await session.commit()
    return True


async def bulk_insert_fund_nav_from_dict(session: AsyncSession, scheme_code: str, nav_data: dict):
    """
    Insert NAV data from dictionary format: {"YYYY-MM-DD": nav_value, ...}
    Converts date strings from YYYY-MM-DD format to date objects.
    Filters out records with invalid NAV values (zero or negative).
    Ensures no duplicates: for each scheme_code + nav_date combination, only one entry is kept.
    Compatible with TimescaleDB using PostgreSQL's ON CONFLICT DO UPDATE.
    """
    if not nav_data:
        return 0
    
    rows = []
    seen_dates = set()  # Track dates to avoid duplicates within the same bulk insert
    skipped_count = 0
    
    for date_str, nav_value in nav_data.items():
        try:
            # Parse date from YYYY-MM-DD format
            nav_date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            nav_float = float(nav_value)
            
            # Skip records with invalid NAV values (must be positive)
            if nav_float <= 0:
                skipped_count += 1
                continue
            
            # Skip duplicate dates within the same bulk insert (keep first occurrence)
            date_key = (scheme_code, nav_date_obj)
            if date_key in seen_dates:
                skipped_count += 1
                continue
            
            seen_dates.add(date_key)
            rows.append({
                "scheme_code": scheme_code,
                "nav_date": nav_date_obj,
                "nav_value": nav_float
            })
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid date format '{date_str}' (expected YYYY-MM-DD) or NAV value '{nav_value}': {str(e)}")
    
    # Only insert if we have valid rows
    if not rows:
        return 0
    
    # Use PostgreSQL ON CONFLICT for upsert with TimescaleDB compatibility
    # This ensures that for each scheme_code + nav_date combination, only one entry exists
    stmt = pg_insert(FundNavHistory).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=['scheme_code', 'nav_date'],
        set_=dict(nav_value=stmt.excluded.nav_value)
    )
    await session.execute(stmt)
    await session.commit()
    return len(rows)


async def delete_fund_nav_history(session: AsyncSession, scheme_code: str, nav_date: Optional[str] = None):
    q = delete(FundNavHistory).where(FundNavHistory.scheme_code == scheme_code)
    if nav_date:
        try:
            nav_date_obj = date_type.fromisoformat(nav_date)
            q = q.where(FundNavHistory.nav_date == nav_date_obj)
        except (ValueError, TypeError):
            # If date parsing fails, return empty list
            return []
    q = q.returning(FundNavHistory)
    res = await session.execute(q)
    await session.commit()
    return res.scalars().all()


# ============================================================================
# BENCHMARK MASTER CRUD OPERATIONS
# ============================================================================

async def create_benchmark_master(session: AsyncSession, benchmark_in: BenchmarkMasterCreate):
    stmt = insert(BenchmarkMaster).values(**benchmark_in.model_dump()).returning(BenchmarkMaster)
    res = await session.execute(stmt)
    await session.commit()
    return res.scalar_one()


async def get_benchmark_master(session: AsyncSession, benchmark_code: str):
    q = select(BenchmarkMaster).where(BenchmarkMaster.benchmark_code == benchmark_code)
    res = await session.execute(q)
    return res.scalar_one_or_none()


async def get_all_benchmark_masters(session: AsyncSession, is_active: Optional[bool] = None):
    q = select(BenchmarkMaster)
    if is_active is not None:
        q = q.where(BenchmarkMaster.is_active == is_active)
    res = await session.execute(q)
    return res.scalars().all()


async def update_benchmark_master(session: AsyncSession, benchmark_code: str, benchmark_in: BenchmarkMasterUpdate):
    data = benchmark_in.model_dump(exclude_unset=True)
    if not data:
        return await get_benchmark_master(session, benchmark_code)
    stmt = (
        update(BenchmarkMaster)
        .where(BenchmarkMaster.benchmark_code == benchmark_code)
        .values(**data)
        .returning(BenchmarkMaster)
    )
    res = await session.execute(stmt)
    await session.commit()
    return res.scalar_one_or_none()


async def delete_benchmark_master(session: AsyncSession, benchmark_code: str):
    stmt = delete(BenchmarkMaster).where(BenchmarkMaster.benchmark_code == benchmark_code).returning(BenchmarkMaster)
    res = await session.execute(stmt)
    await session.commit()
    return res.scalar_one_or_none()


# ============================================================================
# BENCHMARK NAV HISTORY CRUD OPERATIONS
# ============================================================================

async def create_benchmark_nav_history(session: AsyncSession, nav_in: BenchmarkNavHistoryCreate):
    stmt = insert(BenchmarkNavHistory).values(**nav_in.model_dump()).returning(BenchmarkNavHistory)
    res = await session.execute(stmt)
    await session.commit()
    return res.scalar_one()


async def get_benchmark_nav_history(session: AsyncSession, benchmark_code: str, nav_date: Optional[str] = None):
    q = select(BenchmarkNavHistory).where(BenchmarkNavHistory.benchmark_code == benchmark_code)
    if nav_date:
        try:
            nav_date_obj = date_type.fromisoformat(nav_date)
            q = q.where(BenchmarkNavHistory.nav_date == nav_date_obj)
        except (ValueError, TypeError):
            return []
    q = q.order_by(BenchmarkNavHistory.nav_date.desc())
    res = await session.execute(q)
    return res.scalars().all()


async def get_benchmark_nav_by_date_range(session: AsyncSession, benchmark_code: str, start_date: str, end_date: str):
    try:
        start_date_obj = date_type.fromisoformat(start_date)
        end_date_obj = date_type.fromisoformat(end_date)
    except (ValueError, TypeError):
        return []
    
    q = select(BenchmarkNavHistory).where(
        (BenchmarkNavHistory.benchmark_code == benchmark_code) &
        (BenchmarkNavHistory.nav_date >= start_date_obj) &
        (BenchmarkNavHistory.nav_date <= end_date_obj)
    ).order_by(BenchmarkNavHistory.nav_date.desc())
    res = await session.execute(q)
    return res.scalars().all()


async def bulk_insert_benchmark_nav_history(session: AsyncSession, rows: list[dict]):
    if not rows:
        return True
    # Use PostgreSQL ON CONFLICT for upsert
    stmt = pg_insert(BenchmarkNavHistory).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=['benchmark_code', 'nav_date'],
        set_=dict(index_value=stmt.excluded.index_value)
    )
    await session.execute(stmt)
    await session.commit()
    return True


async def bulk_insert_benchmark_nav_from_dict(session: AsyncSession, benchmark_code: str, nav_data: dict):
    """
    Insert benchmark NAV data from dictionary format: {"YYYY-MM-DD": index_value, ...}
    Converts date strings from YYYY-MM-DD format to date objects.
    Filters out records with invalid index values (zero or negative).
    Ensures no duplicates: for each benchmark_code + nav_date combination, only one entry is kept.
    Compatible with TimescaleDB using PostgreSQL's ON CONFLICT DO UPDATE.
    """
    if not nav_data:
        return 0
    
    rows = []
    seen_dates = set()  # Track dates to avoid duplicates within the same bulk insert
    skipped_count = 0
    
    for date_str, index_value in nav_data.items():
        try:
            # Parse date from YYYY-MM-DD format
            nav_date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            index_float = float(index_value)
            
            # Skip records with invalid index values (must be positive)
            if index_float <= 0:
                skipped_count += 1
                continue
            
            # Skip duplicate dates within the same bulk insert (keep first occurrence)
            date_key = (benchmark_code, nav_date_obj)
            if date_key in seen_dates:
                skipped_count += 1
                continue
            
            seen_dates.add(date_key)
            rows.append({
                "benchmark_code": benchmark_code,
                "nav_date": nav_date_obj,
                "index_value": index_float
            })
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid date format '{date_str}' (expected YYYY-MM-DD) or index value '{index_value}': {str(e)}")
    
    # Only insert if we have valid rows
    if not rows:
        return 0
    
    # Use PostgreSQL ON CONFLICT for upsert with TimescaleDB compatibility
    # This ensures that for each benchmark_code + nav_date combination, only one entry exists
    stmt = pg_insert(BenchmarkNavHistory).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=['benchmark_code', 'nav_date'],
        set_=dict(index_value=stmt.excluded.index_value)
    )
    await session.execute(stmt)
    await session.commit()
    return len(rows)


async def delete_benchmark_nav_history(session: AsyncSession, benchmark_code: str, nav_date: Optional[str] = None):
    q = delete(BenchmarkNavHistory).where(BenchmarkNavHistory.benchmark_code == benchmark_code)
    if nav_date:
        try:
            nav_date_obj = date_type.fromisoformat(nav_date)
            q = q.where(BenchmarkNavHistory.nav_date == nav_date_obj)
        except (ValueError, TypeError):
            return []
    q = q.returning(BenchmarkNavHistory)
    res = await session.execute(q)
    await session.commit()
    return res.scalars().all()
