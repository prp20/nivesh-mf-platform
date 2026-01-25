🔹 Mutual Fund APIs
GET     /api/v1/funds
POST    /api/v1/funds
GET     /api/v1/funds/{fund_id}
PUT     /api/v1/funds/{fund_id}
DELETE  /api/v1/funds/{fund_id}

🔹 Fund Manager APIs
GET     /api/v1/fund-managers
POST    /api/v1/fund-managers
GET     /api/v1/fund-managers/{manager_id}
PUT     /api/v1/fund-managers/{manager_id}
DELETE  /api/v1/fund-managers/{manager_id}

🔹 Fund ↔ Manager Mapping APIs
POST    /api/v1/funds/{fund_id}/managers/{manager_id}
DELETE  /api/v1/funds/{fund_id}/managers/{manager_id}
GET     /api/v1/funds/{fund_id}/managers

🔹 NAV APIs (Fund NAV)
POST    /api/v1/nav/fetch/daily
POST    /api/v1/nav/fetch/historical
GET     /api/v1/nav/{fund_id}
DELETE  /api/v1/nav/{fund_id}

🔹 Benchmark NAV APIs
POST    /api/v1/benchmarks/nav/fetch
GET     /api/v1/benchmarks/{benchmark_name}/nav
DELETE  /api/v1/benchmarks/{benchmark_name}/nav

🔹 Analytics / Metrics APIs
GET     /api/v1/metrics/{fund_id}
GET     /api/v1/metrics/{fund_id}/history
POST    /api/v1/metrics/recompute/{fund_id}
DELETE  /api/v1/metrics/{fund_id}

🔹 Comparison APIs
GET     /api/v1/compare?fund_ids=1,2,3

🔹 Recommendation API
POST    /api/v1/recommend

🔹 Utility APIs
GET     /api/v1/health
GET     /api/v1/meta/categories
GET     /api/v1/meta/benchmarks