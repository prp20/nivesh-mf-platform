#!/usr/bin/env python3
"""
download_mf_historical_data.py - Download historical NAV data for mutual funds

Fetches historical Net Asset Value (NAV) data from MFAPI and stores it in TimescaleDB
"""

import sys
import requests
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.db.session import TimeScaleDBSessionLocal
from backend.models.nav_data import NavData
from backend.models.mutual_fund import MutualFund
from analytics.nav_providers.mfapi import MFAPIProvider


def download_historical_nav(fund_scheme_code: str, days: int = 365) -> pd.DataFrame:
    """
    Download historical NAV data for a fund
    
    Args:
        fund_scheme_code: AMFI scheme code (e.g., "120496")
        days: Number of days of history to fetch
    
    Returns:
        DataFrame with columns: date, nav
    """
    print(f"Downloading historical NAV for scheme {fund_scheme_code}...")
    
    try:
        provider = MFAPIProvider()
        nav_data = provider.get_nav_data(fund_scheme_code)
        
        if nav_data is None or nav_data.empty:
            print(f"  ✗ No data found for scheme {fund_scheme_code}")
            return None
        
        # Filter to requested number of days
        nav_data['date'] = pd.to_datetime(nav_data['date'])
        cutoff_date = datetime.now() - timedelta(days=days)
        nav_data = nav_data[nav_data['date'] >= cutoff_date]
        
        print(f"  ✓ Downloaded {len(nav_data)} records")
        return nav_data
    
    except Exception as e:
        print(f"  ✗ Error downloading data: {e}")
        return None

def store_nav_data(fund_id: int, nav_data: pd.DataFrame, db: Session) -> bool:
    """
    Store NAV data in TimescaleDB
    
    Args:
        fund_id: ID of the mutual fund
        nav_data: DataFrame with date and nav columns
        db: Database session
    
    Returns:
        True if successful, False otherwise
    """
    try:
        for _, row in nav_data.iterrows():
            nav_record = NavData(
                fund_id=fund_id,
                nav=float(row['nav']),
                date=row['date'].date(),
                created_at=datetime.now()
            )
            db.add(nav_record)
        
        db.commit()
        print(f"  ✓ Stored {len(nav_data)} NAV records in database")
        return True
    
    except Exception as e:
        db.rollback()
        print(f"  ✗ Error storing data: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("Mutual Fund Historical Data Download Utility")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python download_mf_historical_data.py <scheme_code> [days]")
        print()
        print("Arguments:")
        print("  scheme_code  - AMFI scheme code (e.g., '120496')")
        print("  days         - Number of days to download (default: 365)")
        print()
        print("Example:")
        print("  python download_mf_historical_data.py 120496")
        print("  python download_mf_historical_data.py 120496 730")
        sys.exit(1)
    
    scheme_code = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 365
    
    print(f"Downloading {days} days of NAV data for scheme {scheme_code}...")
    print()
    
    # Download data
    nav_data = download_historical_nav(scheme_code, days)
    if nav_data is None or nav_data.empty:
        print("Failed to download NAV data")
        sys.exit(1)
    
    # Store in database
    db = TimeScaleDBSessionLocal()
    try:
        # For demo, store with fund_id = 1 (adjust as needed)
        fund_id = 1
        success = store_nav_data(fund_id, nav_data, db)
        
        if not success:
            sys.exit(1)
    
    finally:
        db.close()
    
    print()
    print("=" * 60)
    print("Download Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
