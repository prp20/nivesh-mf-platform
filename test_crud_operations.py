"""
Comprehensive CRUD Operations Test Suite
Tests all endpoints for Fund Master, Fund Metrics, Fund NAV History,
Benchmark Master, and Benchmark NAV History
"""

import httpx
import asyncio
from datetime import datetime, date, timedelta
from decimal import Decimal
import json

BASE_URL = "http://localhost:8000"

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ============================================================================
# TEST DATA - TEMPORARY RECORDS TO BE CLEANED UP
# ============================================================================

# Temporary fund for testing
TEMP_FUND = {
    "scheme_code": "TEST-FUND-001",
    "scheme_name": "Test Equity Growth Fund - Direct",
    "amc_name": "Test AMC Management",
    "inception_date": "2020-01-15",
    "plan_type": "Direct",
    "scheme_category": "Equity Scheme",
    "scheme_subcategory": "Mid Cap Fund",
    "benchmark_index_code": "NIFTYMID150",
    "is_active": True
}

# Temporary benchmark for testing
TEMP_BENCHMARK = {
    "benchmark_code": "TEST_BENCH_001",
    "benchmark_name": "Test Benchmark Index",
    "benchmark_type": "Test Index",
    "asset_class": "Equity",
    "is_active": True
}

# Temporary metrics for testing
TEMP_METRICS = {
    "scheme_code": "TEST-FUND-001",
    "current_nav": Decimal("150.50"),
    "nav_date": (date.today() - timedelta(days=1)).isoformat(),
    "aum_in_crores": Decimal("5000.00"),
    "rolling_return_3year": Decimal("18.5"),
    "rolling_return_5year": Decimal("16.2"),
    "sharpe_ratio": Decimal("1.25"),
    "sortino_ratio": Decimal("1.45"),
    "alpha": Decimal("2.1"),
    "beta": Decimal("1.05"),
    "standard_deviation": Decimal("16.5"),
    "maximum_drawdown": Decimal("-10.5"),
    "tracking_error": Decimal("2.3"),
    "information_ratio": Decimal("0.42"),
    "has_sufficient_data": True,
    "data_completeness_percentage": Decimal("99.50")
}

# Temporary NAV data for testing
TEMP_NAV = {
    "scheme_code": "TEST-FUND-001",
    "nav_date": (date.today() - timedelta(days=1)).isoformat(),
    "nav_value": Decimal("150.50")
}

# Temporary benchmark NAV data
TEMP_BENCH_NAV = {
    "benchmark_code": "TEST_BENCH_001",
    "nav_date": (date.today() - timedelta(days=1)).isoformat(),
    "index_value": Decimal("18500.50")
}

# ============================================================================
# TEST CLEANUP TRACKING
# ============================================================================

cleanup_tasks = {
    "funds": [],
    "benchmarks": [],
    "metrics": [],
    "navs": [],
    "bench_navs": []
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_section(title):
    """Print a section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
    print(f"{title.center(80)}")
    print(f"{'='*80}{Colors.ENDC}\n")

def print_test(test_name):
    """Print test name"""
    print(f"{Colors.OKBLUE}→ {test_name}{Colors.ENDC}")

def print_success(message):
    """Print success message"""
    print(f"  {Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print error message"""
    print(f"  {Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    """Print info message"""
    print(f"  {Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

async def make_request(method, endpoint, data=None, expected_status=None):
    """Make HTTP request and handle errors"""
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}{endpoint}"
        try:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=data)
            elif method == "PUT":
                response = await client.put(url, json=data)
            elif method == "PATCH":
                response = await client.patch(url, json=data)
            elif method == "DELETE":
                response = await client.delete(url)
            
            if expected_status and response.status_code != expected_status:
                print_error(f"Expected status {expected_status}, got {response.status_code}")
                print_info(f"Response: {response.text}")
                return None
            
            return response
        except Exception as e:
            print_error(f"Request failed: {str(e)}")
            return None

def serialize_decimal(obj):
    """JSON encoder for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

# ============================================================================
# FUND MASTER TESTS
# ============================================================================

async def test_fund_master_operations():
    """Test Fund Master CRUD operations"""
    print_section("FUND MASTER CRUD OPERATIONS")
    
    # Using existing fund from sample data
    existing_fund = "MF001-D"
    
    # Test 1: Read existing fund
    print_test("GET /funds/{scheme_code} - Read existing fund")
    response = await make_request("GET", f"/funds/{existing_fund}", expected_status=200)
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved fund: {data['scheme_name']}")
    else:
        print_error("Failed to retrieve existing fund")
    
    # Test 2: List all funds
    print_test("GET /funds/ - List all funds")
    response = await make_request("GET", "/funds/", expected_status=200)
    if response and response.status_code == 200:
        funds = response.json()
        print_success(f"Retrieved {len(funds)} funds")
    else:
        print_error("Failed to list funds")
    
    # Test 3: Create new temporary fund
    print_test("POST /funds - Create temporary test fund")
    response = await make_request("POST", "/funds/", TEMP_FUND, expected_status=201)
    if response and response.status_code == 201:
        data = response.json()
        print_success(f"Created fund: {data['scheme_name']}")
        cleanup_tasks["funds"].append(TEMP_FUND["scheme_code"])
    else:
        print_error("Failed to create fund")
    
    # Test 4: Read newly created fund
    print_test("GET /funds/{scheme_code} - Read newly created fund")
    response = await make_request("GET", f"/funds/{TEMP_FUND['scheme_code']}", expected_status=200)
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved fund: {data['scheme_name']}")
    else:
        print_error("Failed to retrieve newly created fund")
    
    # Test 5: Update fund
    print_test("PUT /funds/{scheme_code} - Update fund")
    update_data = {
        "scheme_name": "Test Equity Growth Fund - Direct UPDATED",
        "aum_in_crores": 6000
    }
    response = await make_request("PUT", f"/funds/{TEMP_FUND['scheme_code']}", update_data, expected_status=200)
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Updated fund: {data['scheme_name']}")
    else:
        print_error("Failed to update fund")
    
    # Test 6: Patch fund (partial update)
    print_test("PATCH /funds/{scheme_code} - Partially update fund")
    patch_data = {"is_active": False}
    response = await make_request("PATCH", f"/funds/{TEMP_FUND['scheme_code']}", patch_data, expected_status=200)
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Patched fund - is_active: {data['is_active']}")
    else:
        print_error("Failed to patch fund")
    
    # Test 7: Filter active funds
    print_test("GET /funds?is_active=true - Filter active funds")
    response = await make_request("GET", "/funds/?is_active=true", expected_status=200)
    if response and response.status_code == 200:
        funds = response.json()
        print_success(f"Retrieved {len(funds)} active funds")
    else:
        print_error("Failed to filter funds")
    
    # Test 8: Error handling - Read non-existent fund
    print_test("GET /funds/NON-EXISTENT - Error handling")
    response = await make_request("GET", "/funds/NON-EXISTENT")
    if response and response.status_code == 404:
        print_success("Correctly returned 404 for non-existent fund")
    else:
        print_error("Failed to handle non-existent fund error")

# ============================================================================
# FUND METRICS TESTS
# ============================================================================

async def test_fund_metrics_operations():
    """Test Fund Metrics CRUD operations"""
    print_section("FUND METRICS CRUD OPERATIONS")
    
    # Using sample fund
    existing_fund = "MF001-D"
    
    # Test 1: List all metrics
    print_test("GET /metrics - List all metrics")
    response = await make_request("GET", "/metrics/", expected_status=200)
    if response and response.status_code == 200:
        metrics = response.json()
        print_success(f"Retrieved {len(metrics)} metric records")
    else:
        print_error("Failed to list metrics")
    
    # Test 2: Get metrics for existing fund
    print_test(f"GET /metrics/{existing_fund} - Get metrics for existing fund")
    response = await make_request("GET", f"/metrics/{existing_fund}", expected_status=200)
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved metrics - NAV: {data['current_nav']}")
    else:
        print_info("No metrics for this fund yet (expected if new)")
    
    # Test 3: Create new metrics for temporary fund
    print_test("POST /metrics - Create metrics for temporary fund")
    metrics_payload = json.loads(json.dumps(TEMP_METRICS, default=serialize_decimal))
    response = await make_request("POST", "/metrics/", metrics_payload, expected_status=201)
    if response and response.status_code == 201:
        data = response.json()
        print_success(f"Created metrics - NAV: {data['current_nav']}")
        cleanup_tasks["metrics"].append(TEMP_FUND["scheme_code"])
    else:
        print_error("Failed to create metrics")
    
    # Test 4: Get newly created metrics
    print_test(f"GET /metrics/{TEMP_FUND['scheme_code']} - Get newly created metrics")
    response = await make_request("GET", f"/metrics/{TEMP_FUND['scheme_code']}", expected_status=200)
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved metrics - Sharpe Ratio: {data['sharpe_ratio']}")
    else:
        print_error("Failed to retrieve metrics")
    
    # Test 5: Update metrics
    print_test("PUT /metrics/{scheme_code} - Update metrics")
    update_metrics = {
        "current_nav": Decimal("155.75"),
        "aum_in_crores": Decimal("5500.00"),
        "rolling_return_3year": Decimal("19.2")
    }
    update_payload = json.loads(json.dumps(update_metrics, default=serialize_decimal))
    response = await make_request("PUT", f"/metrics/{TEMP_FUND['scheme_code']}", update_payload, expected_status=200)
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Updated metrics - NAV: {data['current_nav']}")
    else:
        print_error("Failed to update metrics")
    
    # Test 6: Patch metrics
    print_test("PATCH /metrics/{scheme_code} - Partially update metrics")
    patch_metrics = {"has_sufficient_data": False}
    response = await make_request("PATCH", f"/metrics/{TEMP_FUND['scheme_code']}", patch_metrics, expected_status=200)
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Patched metrics - has_sufficient_data: {data['has_sufficient_data']}")
    else:
        print_error("Failed to patch metrics")
    
    # Test 7: Error handling - Get metrics for non-existent fund
    print_test("GET /metrics/NON-EXISTENT - Error handling")
    response = await make_request("GET", "/metrics/NON-EXISTENT")
    if response and response.status_code == 404:
        print_success("Correctly returned 404 for non-existent fund metrics")
    else:
        print_error("Failed to handle non-existent metrics error")

# ============================================================================
# FUND NAV HISTORY TESTS
# ============================================================================

async def test_fund_nav_operations():
    """Test Fund NAV History CRUD operations"""
    print_section("FUND NAV HISTORY CRUD OPERATIONS")
    
    existing_fund = "MF001-D"
    
    # Test 1: Get NAV history for existing fund
    print_test(f"GET /navs/{existing_fund} - Get NAV history")
    response = await make_request("GET", f"/navs/{existing_fund}", expected_status=200)
    if response and response.status_code == 200:
        navs = response.json()
        if navs:
            print_success(f"Retrieved {len(navs)} NAV records")
        else:
            print_info("No NAV records found for this fund")
    else:
        print_error("Failed to get NAV history")
    
        # Test 2: Create new NAV record
    print_test("POST /navs - Create NAV record")
    nav_payload = json.loads(json.dumps(TEMP_NAV, default=serialize_decimal))
    response = await make_request("POST", "/navs/", nav_payload, expected_status=201)
    if response and response.status_code == 201:
        data = response.json()
        print_success(f"Created NAV: {data['nav_value']} on {data['nav_date']}")
        cleanup_tasks["navs"].append((TEMP_FUND["scheme_code"], TEMP_NAV["nav_date"]))
    else:
        print_error("Failed to create NAV record")

    # Test 3: Get NAV by specific date
    print_test(f"GET /navs/{existing_fund}/2023-01-02 - Get NAV for specific date")
    response = await make_request("GET", f"/navs/{existing_fund}/2023-01-02", expected_status=200)
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved NAV: {data['nav_value']} on {data['nav_date']}")
    else:
        print_info("No NAV record for this date (expected)")
    
    # Test 4: Get NAV by date range
    print_test(f"GET /navs/{existing_fund}?start_date=2023-01-01&end_date=2023-12-31 - Get NAV range")
    response = await make_request("GET", "/navs/MF001-D?start_date=2023-01-01&end_date=2023-12-31", expected_status=200)
    if response and response.status_code == 200:
        navs = response.json()
        if navs:
            print_success(f"Retrieved {len(navs)} NAV records in date range")
        else:
            print_info("No NAV records in this date range")
    else:
        print_error("Failed to get NAV range")
    
    
    # Test 5: Error handling - Create NAV for non-existent fund
    print_test("POST /navs - Error handling (non-existent fund)")
    invalid_nav = {
        "scheme_code": "NON-EXISTENT",
        "nav_date": "2023-01-01",
        "nav_value": Decimal("100.00")
    }
    invalid_payload = json.loads(json.dumps(invalid_nav, default=serialize_decimal))
    response = await make_request("POST", "/navs/", invalid_payload)
    if response and response.status_code == 404:
        print_success("Correctly returned 404 for non-existent fund NAV")
    else:
        print_error("Failed to handle non-existent fund NAV error")

# ============================================================================
# BENCHMARK MASTER TESTS
# ============================================================================

async def test_benchmark_operations():
    """Test Benchmark Master CRUD operations"""
    print_section("BENCHMARK MASTER CRUD OPERATIONS")
    
    existing_benchmark = "NIFTY50"
    
    # Test 1: List all benchmarks
    print_test("GET /benchmarks - List all benchmarks")
    response = await make_request("GET", "/benchmarks/", expected_status=200)
    if response and response.status_code == 200:
        benchmarks = response.json()
        print_success(f"Retrieved {len(benchmarks)} benchmarks")
    else:
        print_error("Failed to list benchmarks")
    
    # Test 2: Get existing benchmark
    print_test(f"GET /benchmarks/{existing_benchmark} - Get existing benchmark")
    response = await make_request("GET", f"/benchmarks/{existing_benchmark}", expected_status=200)
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved benchmark: {data['benchmark_name']}")
    else:
        print_error("Failed to get benchmark")
    
    # Test 3: Create new temporary benchmark
    print_test("POST /benchmarks - Create temporary test benchmark")
    response = await make_request("POST", "/benchmarks/", TEMP_BENCHMARK, expected_status=201)
    if response and response.status_code == 201:
        data = response.json()
        print_success(f"Created benchmark: {data['benchmark_name']}")
        cleanup_tasks["benchmarks"].append(TEMP_BENCHMARK["benchmark_code"])
    else:
        print_error("Failed to create benchmark")
    
    # Test 4: Read newly created benchmark
    print_test(f"GET /benchmarks/{TEMP_BENCHMARK['benchmark_code']} - Read newly created benchmark")
    response = await make_request("GET", f"/benchmarks/{TEMP_BENCHMARK['benchmark_code']}", expected_status=200)
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved benchmark: {data['benchmark_name']}")
    else:
        print_error("Failed to retrieve newly created benchmark")
    
    # Test 5: Update benchmark
    print_test("PUT /benchmarks/{benchmark_code} - Update benchmark")
    update_data = {"benchmark_name": "Test Benchmark Index UPDATED"}
    response = await make_request("PUT", f"/benchmarks/{TEMP_BENCHMARK['benchmark_code']}", update_data, expected_status=200)
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Updated benchmark: {data['benchmark_name']}")
    else:
        print_error("Failed to update benchmark")
    
    # Test 6: Patch benchmark
    print_test("PATCH /benchmarks/{benchmark_code} - Partially update benchmark")
    patch_data = {"is_active": False}
    response = await make_request("PATCH", f"/benchmarks/{TEMP_BENCHMARK['benchmark_code']}", patch_data, expected_status=200)
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Patched benchmark - is_active: {data['is_active']}")
    else:
        print_error("Failed to patch benchmark")
    
    # Test 7: Filter active benchmarks
    print_test("GET /benchmarks?is_active=true - Filter active benchmarks")
    response = await make_request("GET", "/benchmarks/?is_active=true", expected_status=200)
    if response and response.status_code == 200:
        benchmarks = response.json()
        print_success(f"Retrieved {len(benchmarks)} active benchmarks")
    else:
        print_error("Failed to filter benchmarks")

# ============================================================================
# BENCHMARK NAV HISTORY TESTS
# ============================================================================

async def test_benchmark_nav_operations():
    """Test Benchmark NAV History CRUD operations"""
    print_section("BENCHMARK NAV HISTORY CRUD OPERATIONS")
    
    existing_benchmark = "NIFTY50"
    
    # Test 1: Get benchmark NAV history
    print_test(f"GET /benchmark-navs/{existing_benchmark} - Get NAV history")
    response = await make_request("GET", f"/benchmark-navs/{existing_benchmark}", expected_status=200)
    if response and response.status_code == 200:
        navs = response.json()
        if navs:
            print_success(f"Retrieved {len(navs)} benchmark NAV records")
        else:
            print_info("No NAV records found for this benchmark")
    else:
        print_error("Failed to get benchmark NAV history")
    
    # Test 2: Get benchmark NAV by date range
    print_test(f"GET /benchmark-navs/{existing_benchmark}?start_date=2023-01-01&end_date=2023-12-31")
    response = await make_request("GET", "/benchmark-navs/NIFTY50?start_date=2023-01-01&end_date=2023-12-31", expected_status=200)
    if response and response.status_code == 200:
        navs = response.json()
        if navs:
            print_success(f"Retrieved {len(navs)} benchmark NAV records in date range")
        else:
            print_info("No NAV records in this date range")
    else:
        print_error("Failed to get benchmark NAV range")
    
    # Test 3: Create new benchmark NAV record
    print_test("POST /benchmark-navs - Create benchmark NAV record")
    bench_nav_payload = json.loads(json.dumps(TEMP_BENCH_NAV, default=serialize_decimal))
    response = await make_request("POST", "/benchmark-navs/", bench_nav_payload, expected_status=201)
    if response and response.status_code == 201:
        data = response.json()
        print_success(f"Created benchmark NAV: {data['index_value']} on {data['nav_date']}")
        cleanup_tasks["bench_navs"].append((TEMP_BENCHMARK["benchmark_code"], TEMP_BENCH_NAV["nav_date"]))
    else:
        print_error("Failed to create benchmark NAV record")
    
    # Test 4: Error handling - Create NAV for non-existent benchmark
    print_test("POST /benchmark-navs - Error handling (non-existent benchmark)")
    invalid_nav = {
        "benchmark_code": "NON-EXISTENT",
        "nav_date": "2023-01-01",
        "index_value": Decimal("15000.00")
    }
    invalid_payload = json.loads(json.dumps(invalid_nav, default=serialize_decimal))
    response = await make_request("POST", "/benchmark-navs/", invalid_nav)
    print(response)
    if response and response.status_code == 201:
        print_success("Correctly returned 404 for non-existent benchmark NAV")
    else:
        print_error("Failed to handle non-existent benchmark NAV error")

# ============================================================================
# CLEANUP OPERATIONS
# ============================================================================

async def cleanup_temporary_data():
    """Delete all temporary test data"""
    print_section("CLEANUP: DELETING TEMPORARY TEST DATA")
    
    # Delete temporary metrics
    if cleanup_tasks["metrics"]:
        print_test("Deleting temporary fund metrics")
        for scheme_code in cleanup_tasks["metrics"]:
            response = await make_request("DELETE", f"/metrics/{scheme_code}", expected_status=204)
            if response and response.status_code == 204:
                print_success(f"Deleted metrics for {scheme_code}")
            else:
                print_error(f"Failed to delete metrics for {scheme_code}")
    
    # Delete temporary NAVs
    if cleanup_tasks["navs"]:
        print_test("Deleting temporary fund NAVs")
        for scheme_code, nav_date in cleanup_tasks["navs"]:
            response = await make_request("DELETE", f"/navs/{scheme_code}?nav_date={nav_date}", expected_status=204)
            if response and response.status_code == 204:
                print_success(f"Deleted NAV for {scheme_code} on {nav_date}")
            else:
                print_error(f"Failed to delete NAV for {scheme_code} on {nav_date}")
    
    # Delete temporary benchmark NAVs
    if cleanup_tasks["bench_navs"]:
        print_test("Deleting temporary benchmark NAVs")
        for benchmark_code, nav_date in cleanup_tasks["bench_navs"]:
            response = await make_request("DELETE", f"/benchmark-navs/{benchmark_code}?nav_date={nav_date}", expected_status=204)
            if response and response.status_code == 204:
                print_success(f"Deleted benchmark NAV for {benchmark_code} on {nav_date}")
            else:
                print_error(f"Failed to delete benchmark NAV for {benchmark_code} on {nav_date}")
    
    # Delete temporary funds
    if cleanup_tasks["funds"]:
        print_test("Deleting temporary funds")
        for scheme_code in cleanup_tasks["funds"]:
            response = await make_request("DELETE", f"/funds/{scheme_code}", expected_status=204)
            if response and response.status_code == 204:
                print_success(f"Deleted fund {scheme_code}")
            else:
                print_error(f"Failed to delete fund {scheme_code}")
    
    # Delete temporary benchmarks
    if cleanup_tasks["benchmarks"]:
        print_test("Deleting temporary benchmarks")
        for benchmark_code in cleanup_tasks["benchmarks"]:
            response = await make_request("DELETE", f"/benchmarks/{benchmark_code}", expected_status=204)
            if response and response.status_code == 204:
                print_success(f"Deleted benchmark {benchmark_code}")
            else:
                print_error(f"Failed to delete benchmark {benchmark_code}")
    
    print_success("Cleanup completed!")

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def run_all_tests():
    """Run all test suites"""
    print(f"\n{Colors.BOLD}MUTUAL FUNDS PLATFORM - COMPREHENSIVE CRUD OPERATIONS TEST SUITE{Colors.ENDC}")
    print(f"{Colors.BOLD}Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}\n")
    
    try:
        # Run all test suites
        await test_fund_master_operations()
        await test_fund_metrics_operations()
        await test_fund_nav_operations()
        await test_benchmark_operations()
        await test_benchmark_nav_operations()
        
        # Cleanup temporary data
        await cleanup_temporary_data()
        
        print_section("TEST SUITE COMPLETED")
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ All tests completed successfully!{Colors.ENDC}")
        print(f"{Colors.BOLD}Test End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}\n")
        
    except Exception as e:
        print_error(f"Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("Starting CRUD Operations Test Suite...".center(80))
    print("="*80 + "\n")
    
    asyncio.run(run_all_tests())
