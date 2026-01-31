"""
Example usage of PostgreSQL + TimescaleDB with the MF Analytics application.

This module demonstrates how to query both regular SQL tables and TimescaleDB hypertables.
"""

from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from backend.db.session import SessionLocal
from backend.models.mutual_fund import MutualFund
from backend.models.nav_data import NavData
from backend.models.benchmark_nav import BenchmarkNav
from backend.models.fund_metrics_snapshot import FundMetricsSnapshot


# ============================================================================
# Regular SQL Queries (Works with both SQLite and PostgreSQL)
# ============================================================================

def get_fund_by_name(fund_name: str) -> MutualFund | None:
    """Get fund by name from regular SQL table."""
    db = SessionLocal()
    try:
        fund = db.query(MutualFund).filter(
            MutualFund.fund_name == fund_name
        ).first()
        return fund
    finally:
        db.close()


def get_all_funds_in_category(category: str) -> list[MutualFund]:
    """Get all funds in a category."""
    db = SessionLocal()
    try:
        funds = db.query(MutualFund).filter(
            MutualFund.category == category
        ).all()
        return funds
    finally:
        db.close()


def get_fund_with_managers(fund_id: int):
    """Get fund with its managers (relationship query)."""
    db = SessionLocal()
    try:
        fund = db.query(MutualFund).filter(
            MutualFund.id == fund_id
        ).first()
        
        if fund:
            # Access relationship
            managers = fund.managers
            return {
                "fund": fund,
                "managers": managers
            }
        return None
    finally:
        db.close()


# ============================================================================
# TimescaleDB Hypertable Queries (Time-Series Optimized)
# ============================================================================

def get_latest_nav(fund_id: int) -> NavData | None:
    """Get the latest NAV for a fund."""
    db = SessionLocal()
    try:
        nav = db.query(NavData).filter(
            NavData.fund_id == fund_id
        ).order_by(NavData.nav_date.desc()).first()
        return nav
    finally:
        db.close()


def get_nav_history(fund_id: int, days: int = 365) -> list[NavData]:
    """Get NAV history for a fund for the last N days."""
    db = SessionLocal()
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        
        navs = db.query(NavData).filter(
            and_(
                NavData.fund_id == fund_id,
                NavData.nav_date >= start_date
            )
        ).order_by(NavData.nav_date).all()
        
        return navs
    finally:
        db.close()


def get_nav_for_date_range(
    fund_id: int,
    start_date,
    end_date
) -> list[NavData]:
    """Get NAV data for a specific date range."""
    db = SessionLocal()
    try:
        navs = db.query(NavData).filter(
            and_(
                NavData.fund_id == fund_id,
                NavData.nav_date >= start_date,
                NavData.nav_date <= end_date
            )
        ).order_by(NavData.nav_date).all()
        
        return navs
    finally:
        db.close()


def get_nav_statistics(fund_id: int, days: int = 365) -> dict:
    """Get NAV statistics (min, max, avg, std dev) for a fund."""
    from sqlalchemy import func, desc
    
    db = SessionLocal()
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        
        stats = db.query(
            func.min(NavData.nav_value).label("min_nav"),
            func.max(NavData.nav_value).label("max_nav"),
            func.avg(NavData.nav_value).label("avg_nav"),
            func.count(NavData.id).label("data_points"),
        ).filter(
            and_(
                NavData.fund_id == fund_id,
                NavData.nav_date >= start_date
            )
        ).first()
        
        if stats:
            return {
                "min_nav": float(stats.min_nav),
                "max_nav": float(stats.max_nav),
                "avg_nav": float(stats.avg_nav),
                "data_points": stats.data_points,
                "date_range": f"Last {days} days"
            }
        return None
    finally:
        db.close()


def get_benchmark_nav(
    benchmark_name: str,
    start_date,
    end_date
) -> list[BenchmarkNav]:
    """Get benchmark NAV for a date range."""
    db = SessionLocal()
    try:
        navs = db.query(BenchmarkNav).filter(
            and_(
                BenchmarkNav.benchmark_name == benchmark_name,
                BenchmarkNav.nav_date >= start_date,
                BenchmarkNav.nav_date <= end_date
            )
        ).order_by(BenchmarkNav.nav_date).all()
        
        return navs
    finally:
        db.close()


def compare_fund_vs_benchmark(
    fund_id: int,
    benchmark_name: str,
    start_date,
    end_date
) -> list[dict]:
    """Compare fund performance vs benchmark."""
    db = SessionLocal()
    try:
        # Get fund NAVs
        fund_navs = db.query(NavData).filter(
            and_(
                NavData.fund_id == fund_id,
                NavData.nav_date >= start_date,
                NavData.nav_date <= end_date
            )
        ).order_by(NavData.nav_date).all()
        
        # Get benchmark NAVs
        bench_navs = db.query(BenchmarkNav).filter(
            and_(
                BenchmarkNav.benchmark_name == benchmark_name,
                BenchmarkNav.nav_date >= start_date,
                BenchmarkNav.nav_date <= end_date
            )
        ).order_by(BenchmarkNav.nav_date).all()
        
        # Create date->nav mapping for benchmark
        bench_map = {nav.nav_date: nav.nav_value for nav in bench_navs}
        
        # Compare
        comparison = []
        for fund_nav in fund_navs:
            bench_nav = bench_map.get(fund_nav.nav_date)
            
            if bench_nav:
                outperformance = (
                    (float(fund_nav.nav_value) - float(bench_nav)) / float(bench_nav) * 100
                )
                
                comparison.append({
                    "date": fund_nav.nav_date,
                    "fund_nav": float(fund_nav.nav_value),
                    "benchmark_nav": float(bench_nav),
                    "outperformance_pct": outperformance
                })
        
        return comparison
    finally:
        db.close()


# ============================================================================
# TimescaleDB Specific Queries (Time-Bucketing)
# ============================================================================

def get_nav_weekly_aggregates(
    fund_id: int,
    weeks: int = 52
) -> list[dict]:
    """
    Get weekly aggregated NAV data using TimescaleDB's time_bucket function.
    
    Note: This requires executing raw SQL as SQLAlchemy doesn't directly support
    TimescaleDB's time_bucket function.
    """
    from sqlalchemy import text
    
    db = SessionLocal()
    try:
        start_date = datetime.now().date() - timedelta(weeks=weeks)
        
        result = db.execute(text("""
            SELECT 
                time_bucket('1 week', nav_date) as week,
                AVG(nav_value) as avg_nav,
                MAX(nav_value) as max_nav,
                MIN(nav_value) as min_nav,
                COUNT(*) as data_points
            FROM nav_data
            WHERE fund_id = :fund_id AND nav_date >= :start_date
            GROUP BY week
            ORDER BY week
        """), {"fund_id": fund_id, "start_date": start_date})
        
        aggregates = []
        for row in result:
            aggregates.append({
                "week": row[0],
                "avg_nav": float(row[1]),
                "max_nav": float(row[2]),
                "min_nav": float(row[3]),
                "data_points": row[4]
            })
        
        return aggregates
    finally:
        db.close()


def get_nav_monthly_aggregates(
    fund_id: int,
    months: int = 12
) -> list[dict]:
    """Get monthly aggregated NAV data."""
    from sqlalchemy import text
    
    db = SessionLocal()
    try:
        start_date = datetime.now().date() - timedelta(days=months*30)
        
        result = db.execute(text("""
            SELECT 
                time_bucket('1 month', nav_date) as month,
                AVG(nav_value) as avg_nav,
                MAX(nav_value) as max_nav,
                MIN(nav_value) as min_nav,
                COUNT(*) as data_points
            FROM nav_data
            WHERE fund_id = :fund_id AND nav_date >= :start_date
            GROUP BY month
            ORDER BY month
        """), {"fund_id": fund_id, "start_date": start_date})
        
        aggregates = []
        for row in result:
            aggregates.append({
                "month": row[0],
                "avg_nav": float(row[1]),
                "max_nav": float(row[2]),
                "min_nav": float(row[3]),
                "data_points": row[4]
            })
        
        return aggregates
    finally:
        db.close()


# ============================================================================
# Fund Metrics Queries
# ============================================================================

def get_latest_metrics(fund_id: int) -> FundMetricsSnapshot | None:
    """Get the latest metrics snapshot for a fund."""
    db = SessionLocal()
    try:
        metrics = db.query(FundMetricsSnapshot).filter(
            FundMetricsSnapshot.fund_id == fund_id
        ).order_by(FundMetricsSnapshot.as_of_date.desc()).first()
        
        return metrics
    finally:
        db.close()


def get_metrics_history(fund_id: int, days: int = 365) -> list[FundMetricsSnapshot]:
    """Get historical metrics for a fund."""
    db = SessionLocal()
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        
        metrics = db.query(FundMetricsSnapshot).filter(
            and_(
                FundMetricsSnapshot.fund_id == fund_id,
                FundMetricsSnapshot.as_of_date >= start_date
            )
        ).order_by(FundMetricsSnapshot.as_of_date).all()
        
        return metrics
    finally:
        db.close()


# ============================================================================
# Bulk Operations
# ============================================================================

def insert_nav_data(nav_records: list[dict]) -> int:
    """
    Insert multiple NAV records efficiently.
    
    Each record should be: {
        "fund_id": int,
        "nav_date": date,
        "nav_value": Decimal
    }
    """
    db = SessionLocal()
    try:
        nav_data_objects = [
            NavData(
                fund_id=record["fund_id"],
                nav_date=record["nav_date"],
                nav_value=record["nav_value"]
            )
            for record in nav_records
        ]
        
        db.add_all(nav_data_objects)
        db.commit()
        
        return len(nav_data_objects)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def insert_benchmark_nav_data(nav_records: list[dict]) -> int:
    """
    Insert multiple benchmark NAV records efficiently.
    
    Each record should be: {
        "benchmark_name": str,
        "nav_date": date,
        "nav_value": Decimal
    }
    """
    db = SessionLocal()
    try:
        nav_data_objects = [
            BenchmarkNav(
                benchmark_name=record["benchmark_name"],
                nav_date=record["nav_date"],
                nav_value=record["nav_value"]
            )
            for record in nav_records
        ]
        
        db.add_all(nav_data_objects)
        db.commit()
        
        return len(nav_data_objects)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == "__main__":
    print("PostgreSQL + TimescaleDB Query Examples")
    print("=" * 50)
    
    # Example 1: Get fund
    print("\n1. Get fund by name:")
    fund = get_fund_by_name("SBI Bluechip Fund")
    if fund:
        print(f"   Found: {fund.fund_name} (ID: {fund.id})")
    
    # Example 2: Get all equity funds
    print("\n2. Get all equity funds:")
    equity_funds = get_all_funds_in_category("Equity")
    print(f"   Found {len(equity_funds)} equity funds")
    
    # Example 3: Get latest NAV
    if equity_funds:
        fund_id = equity_funds[0].id
        print(f"\n3. Latest NAV for fund {fund_id}:")
        latest_nav = get_latest_nav(fund_id)
        if latest_nav:
            print(f"   NAV: {latest_nav.nav_value} on {latest_nav.nav_date}")
    
    # Example 4: Get NAV statistics
    print(f"\n4. NAV statistics (1 year) for fund {fund_id}:")
    stats = get_nav_statistics(fund_id, days=365)
    if stats:
        print(f"   {stats}")
    
    # Example 5: Get weekly aggregates
    print(f"\n5. Weekly aggregates for fund {fund_id}:")
    weekly = get_nav_weekly_aggregates(fund_id, weeks=12)
    print(f"   Found {len(weekly)} weeks of data")
