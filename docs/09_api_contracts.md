# API Contracts & Specifications

## Overview
All endpoints return JSON responses. Errors follow RFC 7231 HTTP status codes.

---

## 📊 Mutual Fund APIs

| Method | Endpoint | Purpose | Request | Response |
|--------|----------|---------|---------|----------|
| POST | `/api/v1/funds` | Create fund | `FundCreate` schema | `FundResponse` |
| GET | `/api/v1/funds` | List all funds | — | `[FundResponse]` |
| GET | `/api/v1/funds/{fund_id}` | Get fund details | — | `FundResponse` |
| PUT | `/api/v1/funds/{fund_id}` | Update fund | `FundUpdate` schema | `FundResponse` |
| DELETE | `/api/v1/funds/{fund_id}` | Delete fund | — | 204 No Content |

**FundCreate Schema:**
```json
{
  "scheme_code": "INF200K01MW0",
  "fund_name": "ICICI Prudential Value Discovery Fund",
  "category": "Equity",
  "sub_category": "Flexi Cap",
  "benchmark": "NIFTY 500",
  "aum": 5000.00,
  "ter": 0.65,
  "exit_load": 0.00,
  "stamp_duty": 0.00,
  "fund_house": "ICICI Prudential Asset Management",
  "launch_date": "2010-03-01"
}
```

---

## 👤 Fund Manager APIs

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/fund-managers` | Create manager |
| GET | `/api/v1/fund-managers` | List all managers |
| GET | `/api/v1/fund-managers/{manager_id}` | Get manager details |
| PUT | `/api/v1/fund-managers/{manager_id}` | Update manager |
| DELETE | `/api/v1/fund-managers/{manager_id}` | Delete manager |

---

## 🔗 Fund ↔ Manager Mapping APIs

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/funds/{fund_id}/managers/{manager_id}` | Assign manager to fund |
| DELETE | `/api/v1/funds/{fund_id}/managers/{manager_id}` | Remove manager from fund |
| GET | `/api/v1/funds/{fund_id}/managers` | List managers for a fund |

---

## 📈 NAV APIs (Fund Net Asset Value)

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| POST | `/api/v1/nav/fetch/daily` | Fetch latest NAVs for all funds | `{"status": "queued", "job_id": "..."}` |
| POST | `/api/v1/nav/fetch/historical/{fund_id}` | Fetch historical NAVs for a fund | `{"status": "queued", "job_id": "..."}` |
| GET | `/api/v1/nav/{fund_id}` | Get NAV history for a fund | `[{"nav_date": "2024-01-31", "nav_value": 150.50}]` |

---

## 📊 Benchmark NAV APIs

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/benchmarks/nav/fetch` | Fetch benchmark NAVs |
| GET | `/api/v1/benchmarks/{benchmark_name}/nav` | Get benchmark NAV history |
| DELETE | `/api/v1/benchmarks/{benchmark_name}/nav` | Delete benchmark NAV data |

---

## 🔄 Data Synchronization APIs (NEW)

Async endpoints for syncing data from external providers.

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| POST | `/api/v1/sync/nav-data` | Start NAV sync job | `SyncResponse` (job_id, status) |
| POST | `/api/v1/sync/funds` | Start fund metadata sync | `SyncResponse` (job_id, status) |
| GET | `/api/v1/sync/status/{job_id}` | Get sync job status | `SyncStatusResponse` (progress, message) |

**SyncResponse:**
```json
{
  "status": "queued",
  "message": "NAV data synchronization started",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**SyncStatusResponse:**
```json
{
  "status": "running",
  "progress": 45,
  "message": "Synced 45/100 funds"
}
```

---

## 📉 Analytics / Metrics APIs

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| GET | `/api/v1/metrics/{fund_id}` | Get latest metrics snapshot | `FundMetricsSnapshot` |
| POST | `/api/v1/metrics/jobs/{fund_id}` | Start metrics computation job | `{"job_id": 123, "status": "PENDING"}` |
| GET | `/api/v1/metrics/jobs/{job_id}` | Get metrics job status | `{"job_id": 123, "status": "RUNNING", "progress": 50}` |

**Metrics Job Response:**
```json
{
  "job_id": 1,
  "fund_id": 42,
  "status": "SUCCESS",
  "progress": 100,
  "started_at": "2024-01-31T10:30:00Z",
  "finished_at": "2024-01-31T10:35:00Z",
  "error_message": null
}
```

**Job Status Enum:**
- `PENDING` - Queued, not yet started
- `RUNNING` - Currently processing
- `SUCCESS` - Completed successfully
- `FAILED` - Failed with error

---

## 🎯 Recommendation API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/recommend` | Get fund recommendations by risk profile |

**Request:**
```json
{
  "risk_profile": "medium",
  "investment_horizon_years": 5,
  "category": "Equity",
  "top_n": 5
}
```

**Response:**
```json
{
  "risk_profile": "medium",
  "count": 5,
  "recommendations": [
    {
      "fund_id": 42,
      "fund_name": "Fund A",
      "category": "Equity",
      "score": 85.50,
      "key_metrics": {
        "alpha": 2.35,
        "sharpe": 1.50,
        "sortino": 2.10,
        "beta": 0.95,
        "std_dev": 12.50
      },
      "explanation": "positive alpha indicates manager skill, strong downside risk-adjusted returns"
    }
  ],
  "disclaimer": "Recommendations are for educational purposes only and do not constitute investment advice."
}
```

---

## ⚖️ Comparison APIs

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/compare?fund_ids=1,2,3` | Compare metrics across multiple funds |

**Response:**
```json
{
  "funds": [
    {
      "fund_id": 1,
      "fund_name": "Fund A",
      "metrics": {...}
    },
    {
      "fund_id": 2,
      "fund_name": "Fund B",
      "metrics": {...}
    }
  ]
}
```

---

## 🏥 Utility APIs

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| GET | `/api/v1/health` | System health check | `{"status": "healthy"}` |

---

## Error Handling

All errors return JSON with structure:

```json
{
  "detail": "Fund not found",
  "status_code": 404
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Resource created
- `204` - No content (successful deletion)
- `400` - Bad request (validation error)
- `404` - Resource not found
- `500` - Server error