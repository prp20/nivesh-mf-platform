#!/bin/bash

# setup_database.sh - Initialize PostgreSQL and TimescaleDB

set -e

echo "=================================="
echo "Setting up Mutual Fund Analytics Database"
echo "=================================="

# PostgreSQL Connection Details
POSTGRES_HOST=${POSTGRES_HOST:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5433}
POSTGRES_NAME=${POSTGRES_NAME:-mf_relational}
POSTGRES_USER=${POSTGRES_USER:-mf_user}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-mf_password}
POSTGRES_ADMIN_USER=${POSTGRES_ADMIN_USER:-postgres}

# TimescaleDB Connection Details
TIMESCALEDB_HOST=${TIMESCALEDB_HOST:-localhost}
TIMESCALEDB_PORT=${TIMESCALEDB_PORT:-5432}
TIMESCALEDB_NAME=${TIMESCALEDB_NAME:-mf_timeseries}
TIMESCALEDB_USER=${TIMESCALEDB_USER:-mf_user}
TIMESCALEDB_PASSWORD=${TIMESCALEDB_PASSWORD:-mf_password}
TIMESCALEDB_ADMIN_USER=${TIMESCALEDB_ADMIN_USER:-postgres}

echo "[1/4] Waiting for PostgreSQL to be ready..."
sleep 5

echo "[2/4] Creating PostgreSQL database and user..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_ADMIN_USER" << EOF
CREATE DATABASE $POSTGRES_NAME;
CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';
ALTER ROLE $POSTGRES_USER SET client_encoding TO 'utf8';
ALTER ROLE $POSTGRES_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $POSTGRES_USER SET default_transaction_deferrable TO on;
ALTER ROLE $POSTGRES_USER SET default_transaction_read_committed TO on;
GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_NAME TO $POSTGRES_USER;
EOF

echo "[3/4] Waiting for TimescaleDB to be ready..."
sleep 5

echo "[4/4] Creating TimescaleDB hypertables..."
PGPASSWORD=$TIMESCALEDB_PASSWORD psql -h "$TIMESCALEDB_HOST" -p "$TIMESCALEDB_PORT" -U "$TIMESCALEDB_USER" -d "$TIMESCALEDB_NAME" << EOF
-- NAV Data Hypertable
CREATE TABLE IF NOT EXISTS nav_data (
    time TIMESTAMPTZ NOT NULL,
    fund_id INT NOT NULL,
    nav NUMERIC(10,4) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('nav_data', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_nav_fund_time ON nav_data (fund_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_nav_date ON nav_data (date DESC);

-- Benchmark Data Hypertable
CREATE TABLE IF NOT EXISTS benchmark_nav (
    time TIMESTAMPTZ NOT NULL,
    benchmark_id VARCHAR(100) NOT NULL,
    nav NUMERIC(10,4) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('benchmark_nav', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_benchmark_id_time ON benchmark_nav (benchmark_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_benchmark_date ON benchmark_nav (date DESC);
EOF

echo ""
echo "=================================="
echo "Database setup completed successfully!"
echo "=================================="
echo ""
echo "PostgreSQL Details:"
echo "  Host: $POSTGRES_HOST:$POSTGRES_PORT"
echo "  Database: $POSTGRES_NAME"
echo "  User: $POSTGRES_USER"
echo ""
echo "TimescaleDB Details:"
echo "  Host: $TIMESCALEDB_HOST:$TIMESCALEDB_PORT"
echo "  Database: $TIMESCALEDB_NAME"
echo "  User: $TIMESCALEDB_USER"
echo ""
