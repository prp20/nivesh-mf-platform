# Mutual Funds Analysis API - Endpoints Reference

## API Overview
The API provides comprehensive CRUD operations for managing mutual fund data, performance metrics, NAV history, and benchmark data.

---

## 1. FUND MASTER ENDPOINTS (`/funds`)

### Create Fund
- **POST** `/funds/`
  - Create a new mutual fund master record
  - Request: `FundMasterCreate`
  - Response: `FundMasterRead`

### List Funds
- **GET** `/funds/`
  - List all funds with optional filtering
  - Query Parameters:
    - `is_active` (bool, optional): Filter by active status
  - Response: `List[FundMasterRead]`

### Get Fund by Scheme Code
- **GET** `/funds/{scheme_code}`
  - Get a specific fund by scheme code
  - Path Parameters:
    - `scheme_code`: Fund scheme code
  - Response: `FundMasterRead`

### Update Fund (Full)
- **PUT** `/funds/{scheme_code}`
  - Update all fund details
  - Path Parameters:
    - `scheme_code`: Fund scheme code
  - Request: `FundMasterUpdate`
  - Response: `FundMasterRead`

### Update Fund (Partial)
- **PATCH** `/funds/{scheme_code}`
  - Partially update fund details
  - Path Parameters:
    - `scheme_code`: Fund scheme code
  - Request: `FundMasterUpdate`
  - Response: `FundMasterRead`

### Delete Fund
- **DELETE** `/funds/{scheme_code}`
  - Delete a fund master record
  - Path Parameters:
    - `scheme_code`: Fund scheme code
  - Response: `204 No Content`

---

## 2. FUND METRICS ENDPOINTS (`/metrics`)

### Create/Update Metrics
- **POST** `/metrics/`
  - Create or update fund performance metrics
  - Request: `FundMetricsCreate`
  - Response: `FundMetricsRead`

### List All Metrics
- **GET** `/metrics/`
  - Get all fund metrics (latest records)
  - Response: `List[FundMetricsRead]`

### Get Metrics by Scheme Code
- **GET** `/metrics/{scheme_code}`
  - Get metrics for a specific fund
  - Path Parameters:
    - `scheme_code`: Fund scheme code
  - Response: `FundMetricsRead`

### Update Metrics (Full)
- **PUT** `/metrics/{scheme_code}`
  - Update all metric details
  - Path Parameters:
    - `scheme_code`: Fund scheme code
  - Request: `FundMetricsUpdate`
  - Response: `FundMetricsRead`

### Update Metrics (Partial)
- **PATCH** `/metrics/{scheme_code}`
  - Partially update metric details
  - Path Parameters:
    - `scheme_code`: Fund scheme code
  - Request: `FundMetricsUpdate`
  - Response: `FundMetricsRead`

### Delete Metrics
- **DELETE** `/metrics/{scheme_code}`
  - Delete metrics for a fund
  - Path Parameters:
    - `scheme_code`: Fund scheme code
  - Response: `204 No Content`

---

## 3. FUND NAV HISTORY ENDPOINTS (`/navs`)

### Create NAV Record
- **POST** `/navs/`
  - Create a new NAV history record for a fund
  - Request: `FundNavHistoryCreate`
  - Response: `FundNavHistoryRead`

### Get NAV History
- **GET** `/navs/{scheme_code}`
  - Get NAV history for a fund, optionally filtered by date range
  - Path Parameters:
    - `scheme_code`: Fund scheme code
  - Query Parameters:
    - `start_date` (string, optional): Start date (YYYY-MM-DD)
    - `end_date` (string, optional): End date (YYYY-MM-DD)
  - Response: `List[FundNavHistoryRead]`

### Get NAV by Specific Date
- **GET** `/navs/{scheme_code}/{nav_date}`
  - Get NAV for a specific fund on a specific date
  - Path Parameters:
    - `scheme_code`: Fund scheme code
    - `nav_date`: NAV date (YYYY-MM-DD)
  - Response: `FundNavHistoryRead`

### Bulk Upload NAV Data
- **POST** `/navs/bulk-csv`
  - Upload NAV data from CSV file
  - Expected CSV Columns: scheme_code, nav_date, nav_value
  - Response: `{"inserted": int, "message": string}`

### Delete NAV History
- **DELETE** `/navs/{scheme_code}`
  - Delete NAV history for a fund (all records or specific date)
  - Path Parameters:
    - `scheme_code`: Fund scheme code
  - Query Parameters:
    - `nav_date` (string, optional): Specific date to delete (YYYY-MM-DD)
  - Response: `204 No Content`

---

## 4. BENCHMARK MASTER ENDPOINTS (`/benchmarks`)

### Create Benchmark
- **POST** `/benchmarks/`
  - Create a new benchmark index
  - Request: `BenchmarkMasterCreate`
  - Response: `BenchmarkMasterRead`

### List Benchmarks
- **GET** `/benchmarks/`
  - List all benchmarks with optional filtering
  - Query Parameters:
    - `is_active` (bool, optional): Filter by active status
  - Response: `List[BenchmarkMasterRead]`

### Get Benchmark by Code
- **GET** `/benchmarks/{benchmark_code}`
  - Get a specific benchmark by code
  - Path Parameters:
    - `benchmark_code`: Benchmark code
  - Response: `BenchmarkMasterRead`

### Update Benchmark (Full)
- **PUT** `/benchmarks/{benchmark_code}`
  - Update all benchmark details
  - Path Parameters:
    - `benchmark_code`: Benchmark code
  - Request: `BenchmarkMasterUpdate`
  - Response: `BenchmarkMasterRead`

### Update Benchmark (Partial)
- **PATCH** `/benchmarks/{benchmark_code}`
  - Partially update benchmark details
  - Path Parameters:
    - `benchmark_code`: Benchmark code
  - Request: `BenchmarkMasterUpdate`
  - Response: `BenchmarkMasterRead`

### Delete Benchmark
- **DELETE** `/benchmarks/{benchmark_code}`
  - Delete a benchmark
  - Path Parameters:
    - `benchmark_code`: Benchmark code
  - Response: `204 No Content`

---

## 5. BENCHMARK NAV HISTORY ENDPOINTS (`/benchmark-navs`)

### Create Benchmark NAV Record
- **POST** `/benchmark-navs/`
  - Create a new benchmark NAV history record
  - Request: `BenchmarkNavHistoryCreate`
  - Response: `BenchmarkNavHistoryRead`

### Get Benchmark NAV History
- **GET** `/benchmark-navs/{benchmark_code}`
  - Get NAV history for a benchmark, optionally filtered by date range
  - Path Parameters:
    - `benchmark_code`: Benchmark code
  - Query Parameters:
    - `start_date` (string, optional): Start date (YYYY-MM-DD)
    - `end_date` (string, optional): End date (YYYY-MM-DD)
  - Response: `List[BenchmarkNavHistoryRead]`

### Get Benchmark NAV by Specific Date
- **GET** `/benchmark-navs/{benchmark_code}/{nav_date}`
  - Get NAV for a specific benchmark on a specific date
  - Path Parameters:
    - `benchmark_code`: Benchmark code
    - `nav_date`: NAV date (YYYY-MM-DD)
  - Response: `BenchmarkNavHistoryRead`

### Bulk Upload Benchmark NAV Data
- **POST** `/benchmark-navs/bulk-csv`
  - Upload benchmark NAV data from CSV file
  - Expected CSV Columns: benchmark_code, nav_date, index_value
  - Response: `{"inserted": int, "message": string}`

### Delete Benchmark NAV History
- **DELETE** `/benchmark-navs/{benchmark_code}`
  - Delete NAV history for a benchmark (all records or specific date)
  - Path Parameters:
    - `benchmark_code`: Benchmark code
  - Query Parameters:
    - `nav_date` (string, optional): Specific date to delete (YYYY-MM-DD)
  - Response: `204 No Content`

---

## 6. HEALTH CHECK ENDPOINT

### API Status
- **GET** `/`
  - Health check and API status
  - Response: `{"message": string, "status": string, "documentation": string}`

---

## Data Models Summary

### FundMaster
- scheme_code (str, PK)
- scheme_name (str)
- amc_name (str)
- inception_date (date)
- plan_type (str) - 'Direct' or 'Regular'
- scheme_category (str)
- scheme_subcategory (str, optional)
- benchmark_index_code (str, optional)
- is_active (bool)
- created_at (datetime)
- updated_at (datetime)

### FundMetrics
- scheme_code (str, PK, FK to FundMaster)
- current_nav (Decimal)
- nav_date (date)
- aum_in_crores (Decimal, optional)
- rolling_return_3year (Decimal, optional)
- rolling_return_5year (Decimal, optional)
- sortino_ratio (Decimal, optional)
- sharpe_ratio (Decimal, optional)
- alpha (Decimal, optional)
- beta (Decimal, optional)
- standard_deviation (Decimal, optional)
- maximum_drawdown (Decimal, optional)
- tracking_error (Decimal, optional)
- information_ratio (Decimal, optional)
- metrics_calculated_at (datetime)
- calculation_period_start_date (date, optional)
- calculation_period_end_date (date, optional)
- has_sufficient_data (bool)
- data_completeness_percentage (Decimal, optional)
- updated_at (datetime)

### FundNavHistory
- scheme_code (str, PK, FK to FundMaster)
- nav_date (date, PK)
- nav_value (Decimal)
- created_at (datetime)

### BenchmarkMaster
- benchmark_code (str, PK)
- benchmark_name (str)
- benchmark_type (str, optional)
- asset_class (str, optional)
- is_active (bool)
- created_at (datetime)
- updated_at (datetime)

### BenchmarkNavHistory
- benchmark_code (str, PK, FK to BenchmarkMaster)
- nav_date (date, PK)
- index_value (Decimal)
- created_at (datetime)

---

## Error Responses

All endpoints follow standard HTTP status codes:
- **200**: Success
- **201**: Created
- **204**: No Content
- **400**: Bad Request
- **404**: Not Found
- **500**: Internal Server Error

Errors are returned as JSON:
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Usage Examples

### Create a Fund
```bash
curl -X POST http://localhost:8000/funds/ \
  -H "Content-Type: application/json" \
  -d '{
    "scheme_code": "101949",
    "scheme_name": "HDFC Bank ETF",
    "amc_name": "HDFC Asset Management",
    "inception_date": "2023-01-15",
    "plan_type": "Direct",
    "scheme_category": "Equity",
    "scheme_subcategory": "Index Funds"
  }'
```

### Get Fund NAV History
```bash
curl http://localhost:8000/navs/101949
```

### Get NAV for Date Range
```bash
curl 'http://localhost:8000/navs/101949?start_date=2024-01-01&end_date=2024-12-31'
```

### Upload Bulk NAV Data
```bash
curl -X POST http://localhost:8000/navs/bulk-csv \
  -F "file=@nav_data.csv"
```
