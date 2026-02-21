from sqlalchemy import select, insert, text, update, delete, cast, Date
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
    stmt = insert(FundNavHistory)
    await session.execute(stmt, rows)
    await session.commit()
    return True


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
    stmt = insert(BenchmarkNavHistory)
    await session.execute(stmt, rows)
    await session.commit()
    return True


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
