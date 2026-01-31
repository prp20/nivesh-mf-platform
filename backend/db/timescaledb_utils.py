"""
Database utilities for managing TimescaleDB connection and operations.
"""

import asyncio
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from loguru import logger

from backend.core.config import settings


async def get_async_engine():
    """Create async SQLAlchemy engine for PostgreSQL."""
    database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=40,
    )
    return engine


async def test_database_connection():
    """Test database connectivity."""
    try:
        engine = await get_async_engine()
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.success("✓ Database connection successful")
            await engine.dispose()
            return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False


async def check_timescaledb_extension():
    """Check if TimescaleDB extension is installed."""
    try:
        engine = await get_async_engine()
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'timescaledb'")
            )
            has_timescaledb = result.fetchone() is not None
            await engine.dispose()
            
            if has_timescaledb:
                logger.success("✓ TimescaleDB extension installed")
            else:
                logger.warning("✗ TimescaleDB extension not found")
            
            return has_timescaledb
    except Exception as e:
        logger.error(f"✗ Error checking TimescaleDB: {e}")
        return False


async def list_hypertables():
    """List all hypertables in the database."""
    try:
        engine = await get_async_engine()
        async with engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT table_name, time_column_name, time_interval
                    FROM timescaledb_information.hypertables
                    ORDER BY table_name
                """)
            )
            hypertables = result.fetchall()
            await engine.dispose()
            
            if hypertables:
                logger.info("Hypertables found:")
                for table_name, time_column, time_interval in hypertables:
                    logger.info(f"  - {table_name} (time column: {time_column}, interval: {time_interval})")
            else:
                logger.info("No hypertables found")
            
            return hypertables
    except Exception as e:
        logger.error(f"✗ Error listing hypertables: {e}")
        return []


async def get_database_stats():
    """Get database statistics."""
    try:
        engine = await get_async_engine()
        async with engine.connect() as conn:
            # Table stats
            result = await conn.execute(
                text("""
                    SELECT 
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                        n_live_tup as row_count
                    FROM pg_stat_user_tables
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                """)
            )
            stats = result.fetchall()
            await engine.dispose()
            
            logger.info("Database table statistics:")
            for schema, table, size, rows in stats:
                logger.info(f"  {schema}.{table}: {size} ({rows} rows)")
            
            return stats
    except Exception as e:
        logger.error(f"✗ Error getting database stats: {e}")
        return []


async def vacuum_and_analyze():
    """Run VACUUM and ANALYZE on the database."""
    try:
        engine = await get_async_engine()
        async with engine.begin() as conn:
            logger.info("Running VACUUM...")
            await conn.execute(text("VACUUM ANALYZE"))
            logger.success("✓ VACUUM and ANALYZE completed")
            await engine.dispose()
            return True
    except Exception as e:
        logger.error(f"✗ Error running VACUUM: {e}")
        return False


async def create_compression_policy(table_name: str, older_than: str = "7 days"):
    """Create a compression policy for a hypertable."""
    try:
        engine = await get_async_engine()
        async with engine.connect() as conn:
            # First check if table is a hypertable
            result = await conn.execute(
                text(f"""
                    SELECT table_name FROM timescaledb_information.hypertables
                    WHERE table_name = '{table_name}'
                """)
            )
            
            if not result.fetchone():
                logger.warning(f"Table {table_name} is not a hypertable")
                await engine.dispose()
                return False
            
            # Create compression policy
            await conn.execute(
                text(f"""
                    SELECT add_compression_policy('{table_name}', INTERVAL '{older_than}')
                """)
            )
            logger.success(f"✓ Compression policy created for {table_name}")
            await engine.dispose()
            return True
    except Exception as e:
        logger.error(f"✗ Error creating compression policy: {e}")
        return False


async def main():
    """Run diagnostic checks."""
    logger.info("=" * 50)
    logger.info("TimescaleDB Diagnostic Report")
    logger.info("=" * 50)
    
    # Test connection
    await test_database_connection()
    
    # Check extension
    await check_timescaledb_extension()
    
    # List hypertables
    await list_hypertables()
    
    # Get stats
    await get_database_stats()
    
    logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
