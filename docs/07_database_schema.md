# Database Schema Reference

## Architecture
The system uses a **hybrid approach**:
- **PostgreSQL**: Transactional data (funds, managers, metrics snapshots)
- **TimescaleDB**: Time-series data (NAV, benchmark data)

---

## PostgreSQL Tables

### mutual_funds
Core mutual fund metadata stored in PostgreSQL.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | INT | PRIMARY KEY | Fund identifier |
| scheme_code | VARCHAR(50) | UNIQUE, NOT NULL | AMFI scheme code |
| fund_name | VARCHAR(255) | NOT NULL | Official fund name |
| category | VARCHAR(50) | NOT NULL | Equity / Debt / Hybrid |
| sub_category | VARCHAR(100) | NULLABLE | Large Cap, Mid Cap, etc. |
| benchmark | VARCHAR(100) | NULLABLE | Assigned benchmark index |
| aum | NUMERIC(20,2) | NULLABLE | Assets under management (₹ Cr) |
| ter | NUMERIC(5,2) | NULLABLE | Total expense ratio (%) |
| exit_load | NUMERIC(5,2) | NULLABLE | Exit load (%) |
| stamp_duty | NUMERIC(5,2) | NULLABLE | Stamp duty (%) |
| fund_house | VARCHAR(255) | NULLABLE | Asset management company |
| launch_date | DATE | NULLABLE | Fund launch date |

### fund_managers
Fund manager information.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | INT | PRIMARY KEY | Manager identifier |
| name | VARCHAR(255) | NOT NULL | Manager full name |
| experience_years | INT | NULLABLE | Years of experience |

### fund_manager_mapping
Many-to-many relationship between funds and managers.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| fund_id | INT | FK (mutual_funds.id) | Fund reference |
| manager_id | INT | FK (fund_managers.id) | Manager reference |

### fund_metrics_snapshot
Computed fund metrics snapshots (daily).

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | INT | PRIMARY KEY | Snapshot identifier |
| fund_id | INT | FK (mutual_funds.id), NOT NULL | Fund reference |
| as_of_date | DATE | NOT NULL | Computation date |
| std_deviation | NUMERIC(10,6) | NULLABLE | Annualized standard deviation |
| sharpe_ratio | NUMERIC(10,6) | NULLABLE | Risk-adjusted return (Sharpe) |
| sortino_ratio | NUMERIC(10,6) | NULLABLE | Downside-adjusted return (Sortino) |
| alpha | NUMERIC(10,6) | NULLABLE | Excess return over benchmark |
| beta | NUMERIC(10,6) | NULLABLE | Volatility relative to benchmark |
| r_squared | NUMERIC(10,6) | NULLABLE | Benchmark correlation |
| upside_capture | NUMERIC(10,6) | NULLABLE | Upside capture ratio |
| downside_capture | NUMERIC(10,6) | NULLABLE | Downside capture ratio |
| rolling_return_1y | NUMERIC(10,6) | NULLABLE | 1-year rolling return |
| rolling_return_3y | NUMERIC(10,6) | NULLABLE | 3-year rolling return |

### benchmark_nav (PostgreSQL)
Benchmark metadata reference.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | INT | PRIMARY KEY | Benchmark identifier |
| benchmark_name | VARCHAR(100) | NOT NULL | Index name (e.g., NIFTY 50) |

### metrics_jobs
Background job tracking for metrics computation.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | INT | PRIMARY KEY | Job identifier |
| fund_id | INT | FK (mutual_funds.id) | Fund being processed |
| status | VARCHAR(50) | NOT NULL | PENDING / RUNNING / SUCCESS / FAILED |
| started_at | TIMESTAMP | NULLABLE | Job start time |
| finished_at | TIMESTAMP | NULLABLE | Job completion time |
| error_message | TEXT | NULLABLE | Error details if failed |

---

## TimescaleDB Hypertables

### nav_data
Time-series NAV data for mutual funds (hypertable).

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | INT | PRIMARY KEY | Record identifier |
| fund_id | INT | NOT NULL | Fund reference (FK to PostgreSQL) |
| nav_date | DATE | NOT NULL | NAV date |
| nav_value | NUMERIC(12,6) | NOT NULL | NAV amount |

**Hypertable Configuration:**
- Time column: `nav_date`
- Chunk interval: 7 days
- Unique constraint: (fund_id, nav_date)
- Indexes: (fund_id, nav_date), (nav_date)

### benchmark_nav
Time-series benchmark index data (hypertable).

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | INT | PRIMARY KEY | Record identifier |
| benchmark_name | VARCHAR(100) | NOT NULL | Benchmark identifier |
| nav_date | DATE | NOT NULL | Index date |
| nav_value | NUMERIC(12,6) | NOT NULL | Index value |

**Hypertable Configuration:**
- Time column: `nav_date`
- Chunk interval: 7 days
- Unique constraint: (benchmark_name, nav_date)
- Indexes: (benchmark_name, nav_date), (nav_date)

---

## Key Design Decisions

### 1. Dual Database Approach
- **Why?** NAV data grows rapidly (~1M+ records/year for 100+ funds). TimescaleDB optimizes for write performance and compression.
- **Trade-off:** Added complexity in session management (two DB connections in metrics engine).

### 2. Append-Only NAV Storage
- No updates or deletes on NAV records
- Ensures auditability
- Supports historical restatement tracking

### 3. Metrics Snapshots
- Daily snapshots rather than real-time computation
- Reduces database load
- Enables rollback/audit trails

### 4. Job Tracking
- Async metrics computation requires status tracking
- Supports polling from frontend
- Enables retry logic for failures

---

## Indexing Strategy

### PostgreSQL Indexes
- `mutual_funds(scheme_code)` - Unique, high-selectivity
- `fund_manager_mapping(fund_id, manager_id)` - Many-to-many lookup
- `fund_metrics_snapshot(fund_id, as_of_date DESC)` - Latest metrics retrieval
- `metrics_jobs(fund_id, status)` - Active job filtering

### TimescaleDB Indexes
- Hypertable indexes created automatically
- Additional: `nav_data(nav_date)` for range queries
- Additional: `benchmark_nav(benchmark_name)` for fast benchmark lookups

---

## Data Flow

```
External Sources (MFAPI, AMFI)
    ↓
NAV Sync Endpoint (/api/v1/sync/nav-data)
    ↓
TimescaleDB (nav_data hypertable)
    ↓
Metrics Computation Job
    ↓
PostgreSQL (fund_metrics_snapshot)
    ↓
Frontend (Streamlit) & API responses
```

---

## Migration Strategy

Migrations are managed via Alembic:
- Location: `backend/alembic/versions/`
- Applied via: `alembic upgrade head`
- Tracked in git for reproducibility

See `backend/alembic/versions/` for:
1. Initial schema setup
2. TimescaleDB hypertable creation
3. Metrics jobs table addition