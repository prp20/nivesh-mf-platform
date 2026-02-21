from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import ssl
from .config import settings

# Create async engine with asyncpg driver
DB_URL = "postgresql+asyncpg://mf_admin:mf_secure_password_123@localhost:5432/mutual_fund_db"

# AsyncPG engine configuration
engine = create_async_engine(
    DB_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# dependency
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
