🔹 Mutual Fund APIs <br>
- POST    /api/v1/funds                           (Create fund) <br>
- GET     /api/v1/funds                           (List all funds)<br>
- GET     /api/v1/funds/{fund_id}                 (Get fund by ID)<br>
- PUT     /api/v1/funds/{fund_id}                 (Update fund)<br>
- DELETE  /api/v1/funds/{fund_id}                 (Delete fund)<br>
<br>
🔹 Fund Manager APIs <br>
- POST    /api/v1/fund-managers                   (Create manager)<br>
- GET     /api/v1/fund-managers                   (List all managers)<br>
- GET     /api/v1/fund-managers/{manager_id}      (Get manager by ID)<br>
- PUT     /api/v1/fund-managers/{manager_id}      (Update manager)<br>
- DELETE  /api/v1/fund-managers/{manager_id}      (Delete manager)<br>
<br>
🔹 Fund ↔ Manager Mapping APIs<br>
- POST    /api/v1/funds/{fund_id}/managers/{manager_id}         (Assign manager to fund)<br>
- DELETE  /api/v1/funds/{fund_id}/managers/{manager_id}         (Remove manager from fund)<br>
- GET     /api/v1/funds/{fund_id}/managers                      (List managers for a fund)<br>
<br>
🔹 NAV APIs (Fund NAV)<br>
- POST    /api/v1/nav/fetch/daily                 (Fetch latest NAVs for all funds)<br>
- POST    /api/v1/nav/fetch/historical/{fund_id}  (Fetch historical NAVs for a fund)<br>
- GET     /api/v1/nav/{fund_id}                   (Get NAV history for a fund)<br>
<br>
🔹 Benchmark NAV APIs<br>
- POST    /api/v1/benchmarks/nav/fetch             (Fetch benchmark NAVs)<br>
- GET     /api/v1/benchmarks/{benchmark_name}/nav (Get benchmark NAV history)<br>
- DELETE  /api/v1/benchmarks/{benchmark_name}/nav (Delete benchmark NAV data)<br>
<br>
🔹 Analytics / Metrics APIs<br>
- GET     /api/v1/metrics/{fund_id}                       (Get latest metrics for a fund)<br>
- POST    /api/v1/metrics/jobs/{fund_id}                  (Start metrics computation job)<br>
- GET     /api/v1/metrics/jobs/{job_id}                   (Get metrics job status)<br>
<br>
🔹 Comparison APIs<br>
- GET     /api/v1/compare?fund_ids=1,2,3         (Compare metrics across multiple funds)<br>
<br>
🔹 Recommendation API<br>
- POST    /api/v1/recommend                       (Get fund recommendations based on risk profile)<br>
<br>
🔹 Utility APIs<br>
- GET     /api/v1/health                          (Health check)<br>