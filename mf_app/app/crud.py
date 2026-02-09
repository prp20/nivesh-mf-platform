from sqlalchemy import select, insert, text, update, delete
from .models import Fund, NAV
from .schemas import FundCreate, NAVCreate
from sqlalchemy.ext.asyncio import AsyncSession

async def create_fund(session: AsyncSession, fund_in: FundCreate):
    stmt = insert(Fund).values(**fund_in.dict()).returning(Fund)
    res = await session.execute(stmt)
    await session.commit()
    return res.fetchone()

async def get_fund_by_code(session: AsyncSession, code: str):
    q = select(Fund).where(Fund.scheme_code == code)
    res = await session.execute(q)
    return res.scalar_one_or_none()


async def get_all_funds(session: AsyncSession):
    q = select(Fund)
    res = await session.execute(q)
    return res.scalars().all()


async def update_fund_by_code(session: AsyncSession, code: str, fund_in: FundCreate):
    stmt = (
        update(Fund)
        .where(Fund.scheme_code == code)
        .values(**fund_in.dict())
        .returning(Fund)
    )
    res = await session.execute(stmt)
    await session.commit()
    return res.fetchone()


async def delete_fund_by_code(session: AsyncSession, code: str):
    stmt = delete(Fund).where(Fund.scheme_code == code).returning(Fund)
    res = await session.execute(stmt)
    await session.commit()
    return res.fetchone()

async def insert_nav(session: AsyncSession, nav_in: NAVCreate):
    stmt = insert(NAV).values(**nav_in.dict()).returning(NAV)
    res = await session.execute(stmt)
    await session.commit()
    return res.fetchone()

async def bulk_insert_nav(session: AsyncSession, rows: list[dict]):
    # rows = list of dicts with scheme_code, nav_time, nav_value, source
    stmt = insert(NAV)
    await session.execute(stmt, rows)
    await session.commit()
    return True

# Example of Timescale aggregation via raw SQL: monthly avg NAV for a scheme
async def monthly_avg_nav(session: AsyncSession, scheme_code: str):
    sql = text("""
        SELECT time_bucket('1 month', nav_time) AS month,
               avg(nav_value) AS avg_nav
        FROM nav
        WHERE scheme_code = :code
        GROUP BY month
        ORDER BY month;
    """)
    res = await session.execute(sql, {"code": scheme_code})
    return res.fetchall()
