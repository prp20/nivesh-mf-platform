import time
import logging
from datetime import datetime, timezone
from typing import List, Optional

import pandas as pd
from mftool import Mftool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from . import crud
from .models import FundMaster, FundNavHistory
from .schemas import FundNavHistoryCreate

logger = logging.getLogger(__name__)


async def fetch_all_funds(session: AsyncSession) -> List[FundMaster]:
    """
    Fetch all funds from the database.
    
    Args:
        session: AsyncSession for database operations
        
    Returns:
        List of FundMaster objects
    """
    query = select(FundMaster)
    result = await session.execute(query)
    funds = result.scalars().all()
    return funds


def fetch_nav_data_for_scheme(mf: Mftool, scheme_code: str, retries: int = 3, sleep_sec: float = 0.5) -> Optional[pd.DataFrame]:
    """
    Fetch historical NAV data for a scheme from mftool.
    
    Args:
        mf: Mftool instance
        scheme_code: Scheme code as string
        retries: Number of retries on failure
        sleep_sec: Sleep duration between retries
        
    Returns:
        DataFrame with NAV data (index is date, column is nav values) or None if failed
    """
    for attempt in range(1, retries + 1):
        try:
            nav_df = mf.get_scheme_historical_nav(str(scheme_code), as_Dataframe=True)
            return nav_df
        except Exception as e:
            logger.warning(f"Attempt {attempt}/{retries} failed for scheme {scheme_code}: {e}")
            if attempt == retries:
                logger.error(f"Failed to fetch NAV data for scheme {scheme_code} after {retries} attempts")
                return None
            time.sleep(sleep_sec * attempt)
    return None


def transform_nav_dataframe(nav_df: pd.DataFrame, scheme_code: str) -> List[dict]:
    """
    Transform NAV DataFrame into list of dictionaries for database insertion.
    
    Input DataFrame format:
                 nav
    date
    26-10-2021  81.08400
    25-10-2021  79.60400
    ...
    
    Args:
        nav_df: DataFrame with date index and 'nav' column
        scheme_code: Scheme code for the NAV records
        
    Returns:
        List of dictionaries with keys: scheme_code, nav_date, nav_value
    """
    if nav_df is None or nav_df.empty:
        return []
    
    rows = []
    
    for date_str, row in nav_df.iterrows():
        try:
            # Parse date from index (format: DD-MM-YYYY)
            nav_date = pd.to_datetime(date_str, format="%d-%m-%Y").date()
            
            # Get NAV value from the 'nav' column
            nav_value = float(row['nav'])
            
            rows.append({
                'scheme_code': str(scheme_code),
                'nav_date': nav_date,
                'nav_value': nav_value
            })
        except Exception as e:
            logger.error(f"Error parsing NAV row for {scheme_code}: {e}")
            continue
    
    return rows


async def check_nav_exists(session: AsyncSession, scheme_code: str, nav_date) -> bool:
    """
    Check if a NAV record already exists for a scheme and date.
    
    Args:
        session: AsyncSession for database operations
        scheme_code: Scheme code
        nav_date: NAV date
        
    Returns:
        True if record exists, False otherwise
    """
    query = select(FundNavHistory).where(
        (FundNavHistory.scheme_code == scheme_code) & (FundNavHistory.nav_date == nav_date)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none() is not None


async def push_nav_to_db(session: AsyncSession, nav_rows: List[dict], skip_duplicates: bool = True) -> int:
    """
    Push NAV data to the database using bulk insert.
    
    Args:
        session: AsyncSession for database operations
        nav_rows: List of dictionaries with nav data (scheme_code, nav_date, nav_value)
        skip_duplicates: If True, skip records that already exist in the database
        
    Returns:
        Number of records inserted
    """
    if not nav_rows:
        logger.info("No NAV rows to insert")
        return 0
    
    rows_to_insert = []
    
    if skip_duplicates:
        # Filter out existing records
        for row in nav_rows:
            exists = await check_nav_exists(session, row['scheme_code'], row['nav_date'])
            if not exists:
                rows_to_insert.append(row)
        
        if not rows_to_insert:
            logger.info(f"All {len(nav_rows)} NAV records already exist in database")
            return 0
    else:
        rows_to_insert = nav_rows
    
    try:
        await crud.bulk_insert_fund_nav_history(session, rows_to_insert)
        logger.info(f"Successfully inserted {len(rows_to_insert)} NAV records")
        return len(rows_to_insert)
    except IntegrityError as e:
        logger.warning(f"Duplicate record(s) encountered during insert. Skipping duplicates.")
        await session.rollback()
        return 0
    except Exception as e:
        logger.error(f"Error inserting NAV records: {e}")
        raise


async def fetch_and_push_nav_for_all_funds(
    session: AsyncSession,
    throttle_sec: float = 1.0,
    skip_duplicates: bool = True,
    batch_size: int = 100
) -> dict:
    """
    Main orchestration function: loop through all funds, fetch NAV data, and push to DB.
    
    Args:
        session: AsyncSession for database operations
        throttle_sec: Sleep duration between API calls for rate limiting (default: 1 second)
        skip_duplicates: If True, skip records that already exist
        batch_size: Not used in current implementation, but useful for future batching
        
    Returns:
        Dictionary with statistics: {
            'total_funds': int,
            'successful': int,
            'failed': int,
            'nav_records_inserted': int
        }
    """
    mf = Mftool()
    stats = {
        'total_funds': 0,
        'successful': 0,
        'failed': 0,
        'nav_records_inserted': 0
    }
    
    # Fetch all funds
    funds = await fetch_all_funds(session)
    stats['total_funds'] = len(funds)
    
    logger.info(f"Starting NAV fetch for {stats['total_funds']} funds")
    
    for i, fund in enumerate(funds, 1):
        try:
            logger.info(f"[{i}/{stats['total_funds']}] Processing {fund.scheme_code}: {fund.scheme_name}")
            
            # Fetch NAV data from mftool
            nav_df = fetch_nav_data_for_scheme(mf, fund.scheme_code)
            
            if nav_df is None:
                stats['failed'] += 1
                logger.warning(f"Skipped {fund.scheme_code}: NAV fetch failed")
                time.sleep(throttle_sec)
                continue
            
            # Transform DataFrame into database-ready format
            nav_rows = transform_nav_dataframe(nav_df, fund.scheme_code)
            
            if not nav_rows:
                logger.warning(f"No NAV data returned for {fund.scheme_code}")
                stats['failed'] += 1
                time.sleep(throttle_sec)
                continue
            
            # Push to database
            inserted_count = await push_nav_to_db(session, nav_rows, skip_duplicates=skip_duplicates)
            stats['nav_records_inserted'] += inserted_count
            stats['successful'] += 1
            
            logger.info(f"✓ {fund.scheme_code}: Inserted {inserted_count} NAV records")
            
        except Exception as e:
            logger.error(f"Error processing {fund.scheme_code}: {e}")
            stats['failed'] += 1
        
        # Polite throttling to avoid overwhelming the API
        time.sleep(throttle_sec)
    
    logger.info(f"NAV fetch complete - Successful: {stats['successful']}, Failed: {stats['failed']}, Records inserted: {stats['nav_records_inserted']}")
    
    return stats
