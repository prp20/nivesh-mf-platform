#!/bin/bash

echo "=== Checking Database Connection ==="
docker exec mutual_fund_timescaledb psql -U mf_admin -d mutual_fund_db -c "SELECT version();"

echo ""
echo "=== Checking TimescaleDB Extension ==="
docker exec mutual_fund_timescaledb psql -U mf_admin -d mutual_fund_db -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'timescaledb';"

echo ""
echo "=== Checking Schema ==="
docker exec mutual_fund_timescaledb psql -U mf_admin -d mutual_fund_db -c "\dn"

echo ""
echo "=== Checking Tables ==="
docker exec mutual_fund_timescaledb psql -U mf_admin -d mutual_fund_db -c "\dt mutual_funds.*"

echo ""
echo "=== Checking Hypertables ==="
docker exec mutual_fund_timescaledb psql -U mf_admin -d mutual_fund_db -c "SELECT hypertable_schema, hypertable_name FROM timescaledb_information.hypertables;"

echo ""
echo "=== Checking Sample Data ==="
docker exec mutual_fund_timescaledb psql -U mf_admin -d mutual_fund_db -c "SELECT COUNT(*) as fund_count FROM mutual_funds.fund_master;"
docker exec mutual_fund_timescaledb psql -U mf_admin -d mutual_fund_db -c "SELECT COUNT(*) as benchmark_count FROM mutual_funds.benchmark_master;"

