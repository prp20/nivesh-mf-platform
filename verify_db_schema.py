#!/usr/bin/env python3
"""
verify_db_schema.py - Verify database schema integrity

Validates that both PostgreSQL and TimescaleDB have the correct tables,
columns, and constraints set up properly.
"""

import sys
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from backend.db.session import PostgresSessionLocal, TimeScaleDBSessionLocal
from backend.models.mutual_fund import MutualFund
from backend.models.fund_manager import FundManager
from backend.models.fund_manager_mapping import FundManagerMapping
from backend.models.fund_metrics_snapshot import FundMetricsSnapshot
from backend.models.nav_data import NavData
from backend.models.benchmark_nav import BenchmarkNav


def verify_postgresql():
    """Verify PostgreSQL schema"""
    print("Verifying PostgreSQL Schema...")
    print("-" * 50)
    
    try:
        db = PostgresSessionLocal()
        inspector = inspect(db.get_bind())
        
        required_tables = [
            'mutual_funds',
            'fund_managers',
            'fund_manager_mapping',
            'fund_metrics_snapshot'
        ]
        
        existing_tables = inspector.get_table_names()
        
        for table_name in required_tables:
            if table_name in existing_tables:
                print(f"✓ Table '{table_name}' exists")
                columns = inspector.get_columns(table_name)
                print(f"  Columns: {len(columns)}")
                for col in columns[:3]:
                    print(f"    - {col['name']} ({col['type']})")
                if len(columns) > 3:
                    print(f"    ... and {len(columns)-3} more")
            else:
                print(f"✗ Table '{table_name}' NOT FOUND")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ Error verifying PostgreSQL: {e}")
        return False

def verify_timescaledb():
    """Verify TimescaleDB schema"""
    print("\nVerifying TimescaleDB Schema...")
    print("-" * 50)
    
    try:
        db = TimeScaleDBSessionLocal()
        inspector = inspect(db.get_bind())
        
        required_tables = [
            'nav_data',
            'benchmark_nav'
        ]
        
        existing_tables = inspector.get_table_names()
        
        for table_name in required_tables:
            if table_name in existing_tables:
                print(f"✓ Table '{table_name}' exists")
                columns = inspector.get_columns(table_name)
                print(f"  Columns: {len(columns)}")
                for col in columns[:3]:
                    print(f"    - {col['name']} ({col['type']})")
                if len(columns) > 3:
                    print(f"    ... and {len(columns)-3} more")
                
                # Check if it's a hypertable
                try:
                    result = db.execute(
                        text(f"SELECT tablename FROM _timescaledb_catalog.hypertable WHERE table_name = '{table_name}'")
                    ).fetchone()
                    if result:
                        print(f"  ✓ Configured as TimescaleDB hypertable")
                    else:
                        print(f"  ⚠ Not configured as hypertable")
                except:
                    pass
            else:
                print(f"✗ Table '{table_name}' NOT FOUND")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ Error verifying TimescaleDB: {e}")
        return False

def test_connectivity():
    """Test database connectivity"""
    print("\nTesting Database Connectivity...")
    print("-" * 50)
    
    try:
        print("Testing PostgreSQL connection...", end=" ")
        db_pg = PostgresSessionLocal()
        result = db_pg.execute(text("SELECT 1"))
        assert result.scalar() == 1
        db_pg.close()
        print("✓")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    try:
        print("Testing TimescaleDB connection...", end=" ")
        db_ts = TimeScaleDBSessionLocal()
        result = db_ts.execute(text("SELECT 1"))
        assert result.scalar() == 1
        db_ts.close()
        print("✓")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

def main():
    """Run all verification checks"""
    print("=" * 50)
    print("Database Schema Verification")
    print("=" * 50)
    print()
    
    results = []
    results.append(("Connectivity", test_connectivity()))
    results.append(("PostgreSQL", verify_postgresql()))
    results.append(("TimescaleDB", verify_timescaledb()))
    
    print("\n" + "=" * 50)
    print("Verification Summary")
    print("=" * 50)
    
    for check_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{check_name:20} {status}")
    
    print("=" * 50)
    
    all_passed = all(result for _, result in results)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
