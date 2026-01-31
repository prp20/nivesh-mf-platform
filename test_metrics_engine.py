#!/usr/bin/env python3
"""
test_metrics_engine.py - Unit tests for the metrics engine

Tests the computation of financial metrics:
- Sharpe Ratio
- Sortino Ratio
- Alpha
- Beta
- Maximum Drawdown
- Cumulative Returns
"""

import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Test data generation
def generate_test_nav_data(base_nav=100, days=252, volatility=0.15):
    """Generate synthetic NAV data for testing"""
    dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
    returns = np.random.normal(0.0005, volatility/np.sqrt(252), days)
    navs = base_nav * np.exp(np.cumsum(returns))
    
    return pd.DataFrame({
        'date': dates,
        'nav': navs
    })

def generate_benchmark_data(base_nav=100, days=252, volatility=0.12):
    """Generate synthetic benchmark NAV data"""
    dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
    returns = np.random.normal(0.0004, volatility/np.sqrt(252), days)
    navs = base_nav * np.exp(np.cumsum(returns))
    
    return pd.DataFrame({
        'date': dates,
        'nav': navs
    })

def test_sharpe_ratio():
    """Test Sharpe ratio calculation"""
    print("Testing Sharpe Ratio...")
    try:
        from analytics.metrics_engine import compute_sharpe
        
        nav_data = generate_test_nav_data()
        sharpe = compute_sharpe(nav_data['nav'].values)
        
        assert isinstance(sharpe, (int, float, np.number)), "Sharpe should be numeric"
        assert not np.isnan(sharpe), "Sharpe should not be NaN"
        print(f"  ✓ Sharpe Ratio: {sharpe:.2f}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    return True

def test_sortino_ratio():
    """Test Sortino ratio calculation"""
    print("Testing Sortino Ratio...")
    try:
        from analytics.metrics_engine import compute_sortino
        
        nav_data = generate_test_nav_data()
        sortino = compute_sortino(nav_data['nav'].values)
        
        assert isinstance(sortino, (int, float, np.number)), "Sortino should be numeric"
        assert not np.isnan(sortino), "Sortino should not be NaN"
        print(f"  ✓ Sortino Ratio: {sortino:.2f}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    return True

def test_maximum_drawdown():
    """Test maximum drawdown calculation"""
    print("Testing Maximum Drawdown...")
    try:
        from analytics.metrics_engine import compute_max_drawdown
        
        nav_data = generate_test_nav_data()
        mdd = compute_max_drawdown(nav_data['nav'].values)
        
        assert isinstance(mdd, (int, float, np.number)), "MDD should be numeric"
        assert mdd <= 0, "MDD should be non-positive"
        print(f"  ✓ Max Drawdown: {mdd:.2%}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    return True

def test_cumulative_returns():
    """Test cumulative returns calculation"""
    print("Testing Cumulative Returns...")
    try:
        from analytics.metrics_engine import compute_cumulative_returns
        
        nav_data = generate_test_nav_data()
        returns = compute_cumulative_returns(nav_data['nav'].values)
        
        assert isinstance(returns, (int, float, np.number)), "Returns should be numeric"
        print(f"  ✓ Cumulative Returns: {returns:.2%}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    return True

def test_alpha_beta():
    """Test alpha and beta calculation"""
    print("Testing Alpha & Beta...")
    try:
        from analytics.metrics_engine import compute_alpha, compute_beta
        
        fund_nav = generate_test_nav_data()
        bench_nav = generate_benchmark_data()
        
        beta = compute_beta(fund_nav['nav'].values, bench_nav['nav'].values)
        alpha = compute_alpha(fund_nav['nav'].values, bench_nav['nav'].values)
        
        assert isinstance(beta, (int, float, np.number)), "Beta should be numeric"
        assert isinstance(alpha, (int, float, np.number)), "Alpha should be numeric"
        print(f"  ✓ Beta: {beta:.2f}")
        print(f"  ✓ Alpha: {alpha:.2%}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    return True

def run_all_tests():
    """Run all metric tests"""
    print("="*50)
    print("Metrics Engine Test Suite")
    print("="*50)
    print()
    
    tests = [
        test_sharpe_ratio,
        test_sortino_ratio,
        test_maximum_drawdown,
        test_cumulative_returns,
        test_alpha_beta,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except ImportError as e:
            print(f"✗ Import Error: {e}")
            results.append(False)
        print()
    
    print("="*50)
    passed = sum(results)
    total = len(results)
    print(f"Test Results: {passed}/{total} passed")
    print("="*50)
    
    return all(results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
