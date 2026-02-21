-- ============================================================================
-- MUTUAL FUND ANALYSIS DATABASE INITIALIZATION SCRIPT
-- This script runs automatically when the container first starts
-- ============================================================================

-- Create the mutual_funds schema
CREATE SCHEMA IF NOT EXISTS mutual_funds;

-- Set search path
SET search_path TO mutual_funds, public;

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ============================================================================
-- TABLE 1: FUND MASTER DATA (Static/Semi-static attributes)
-- ============================================================================

CREATE TABLE mutual_funds.fund_master (
    scheme_code VARCHAR(50) PRIMARY KEY,
    scheme_name VARCHAR(500) NOT NULL,
    amc_name VARCHAR(200) NOT NULL,
    inception_date DATE NOT NULL,
    plan_type VARCHAR(20) NOT NULL CHECK (plan_type IN ('Direct', 'Regular')),
    scheme_category VARCHAR(100) NOT NULL,
    scheme_subcategory VARCHAR(100),
    benchmark_index_code VARCHAR(50),
    
    -- Status flags
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_inception_date CHECK (inception_date <= CURRENT_DATE)
);

-- Indexes for fund_master
CREATE INDEX idx_fund_master_amc ON mutual_funds.fund_master(amc_name);
CREATE INDEX idx_fund_master_category ON mutual_funds.fund_master(scheme_category, scheme_subcategory);
CREATE INDEX idx_fund_master_plan_type ON mutual_funds.fund_master(plan_type);
CREATE INDEX idx_fund_master_active ON mutual_funds.fund_master(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_fund_master_benchmark ON mutual_funds.fund_master(benchmark_index_code);

COMMENT ON TABLE mutual_funds.fund_master IS 'Master data for mutual fund schemes - contains static and semi-static attributes that do not change daily';

-- ============================================================================
-- TABLE 2: FUND METRICS (Daily computed performance and risk metrics)
-- ============================================================================

CREATE TABLE mutual_funds.fund_metrics (
    scheme_code VARCHAR(50) PRIMARY KEY REFERENCES mutual_funds.fund_master(scheme_code) ON DELETE CASCADE,
    
    -- Current NAV Information
    current_nav NUMERIC(15,4) NOT NULL,
    nav_date DATE NOT NULL,
    
    -- AUM (Assets Under Management)
    aum_in_crores NUMERIC(18,2),
    
    -- Rolling Returns (Annualized percentages)
    rolling_return_3year NUMERIC(10,4),
    rolling_return_5year NUMERIC(10,4),
    
    -- Risk-Adjusted Return Metrics
    sortino_ratio NUMERIC(10,4),
    sharpe_ratio NUMERIC(10,4),
    
    -- CAPM Metrics
    alpha NUMERIC(10,4),
    beta NUMERIC(10,4),
    
    -- Risk Metrics
    standard_deviation NUMERIC(10,4),
    
    -- Additional Risk Metrics
    maximum_drawdown NUMERIC(10,4),
    tracking_error NUMERIC(10,4),
    information_ratio NUMERIC(10,4),
    
    -- Calculation Metadata
    metrics_calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    calculation_period_start_date DATE,
    calculation_period_end_date DATE,
    
    -- Data Quality Indicators
    has_sufficient_data BOOLEAN DEFAULT TRUE,
    data_completeness_percentage NUMERIC(5,2),
    
    -- Metadata
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_current_nav CHECK (current_nav > 0),
    CONSTRAINT valid_nav_date CHECK (nav_date <= CURRENT_DATE),
    CONSTRAINT valid_aum CHECK (aum_in_crores IS NULL OR aum_in_crores >= 0),
    CONSTRAINT valid_data_completeness CHECK (data_completeness_percentage BETWEEN 0 AND 100)
);

-- Indexes for fund_metrics
CREATE INDEX idx_fund_metrics_nav_date ON mutual_funds.fund_metrics(nav_date DESC);
CREATE INDEX idx_fund_metrics_aum ON mutual_funds.fund_metrics(aum_in_crores DESC NULLS LAST);
CREATE INDEX idx_fund_metrics_3yr_return ON mutual_funds.fund_metrics(rolling_return_3year DESC NULLS LAST);
CREATE INDEX idx_fund_metrics_5yr_return ON mutual_funds.fund_metrics(rolling_return_5year DESC NULLS LAST);
CREATE INDEX idx_fund_metrics_sharpe ON mutual_funds.fund_metrics(sharpe_ratio DESC NULLS LAST);

COMMENT ON TABLE mutual_funds.fund_metrics IS 'Daily computed performance and risk metrics for mutual funds - recomputed daily';

-- ============================================================================
-- TABLE 3: FUND NAV HISTORY (TimescaleDB Hypertable)
-- ============================================================================

CREATE TABLE mutual_funds.fund_nav_history (
    scheme_code VARCHAR(50) NOT NULL REFERENCES mutual_funds.fund_master(scheme_code) ON DELETE CASCADE,
    nav_date DATE NOT NULL,
    nav_value NUMERIC(15,4) NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite primary key
    PRIMARY KEY (scheme_code, nav_date),
    
    CONSTRAINT valid_nav_value CHECK (nav_value > 0),
    CONSTRAINT valid_nav_date_history CHECK (nav_date <= CURRENT_DATE)
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable(
    'mutual_funds.fund_nav_history', 
    'nav_date',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

-- Indexes
CREATE INDEX idx_fund_nav_history_scheme ON mutual_funds.fund_nav_history(scheme_code, nav_date DESC);
CREATE INDEX idx_fund_nav_history_date ON mutual_funds.fund_nav_history(nav_date DESC);

-- Enable compression
ALTER TABLE mutual_funds.fund_nav_history SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'scheme_code',
    timescaledb.compress_orderby = 'nav_date DESC'
);

SELECT add_compression_policy('mutual_funds.fund_nav_history', INTERVAL '90 days');

COMMENT ON TABLE mutual_funds.fund_nav_history IS 'TimescaleDB hypertable storing daily historical NAV data for all mutual fund schemes';

-- ============================================================================
-- TABLE 4: BENCHMARK MASTER DATA
-- ============================================================================

CREATE TABLE mutual_funds.benchmark_master (
    benchmark_code VARCHAR(50) PRIMARY KEY,
    benchmark_name VARCHAR(200) NOT NULL,
    benchmark_type VARCHAR(100),
    ticker VARCHAR(50) NOT NULL,
    asset_class VARCHAR(50),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_benchmark_master_type ON mutual_funds.benchmark_master(benchmark_type);
CREATE INDEX idx_benchmark_master_asset_class ON mutual_funds.benchmark_master(asset_class);
CREATE INDEX idx_benchmark_master_active ON mutual_funds.benchmark_master(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE mutual_funds.benchmark_master IS 'Master data for benchmark indices used for fund performance comparison';

-- ============================================================================
-- TABLE 5: BENCHMARK NAV HISTORY (TimescaleDB Hypertable)
-- ============================================================================

CREATE TABLE mutual_funds.benchmark_nav_history (
    benchmark_code VARCHAR(50) NOT NULL REFERENCES mutual_funds.benchmark_master(benchmark_code) ON DELETE CASCADE,
    nav_date DATE NOT NULL,
    index_value NUMERIC(15,4) NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite primary key
    PRIMARY KEY (benchmark_code, nav_date),
    
    CONSTRAINT valid_index_value CHECK (index_value > 0),
    CONSTRAINT valid_benchmark_nav_date CHECK (nav_date <= CURRENT_DATE)
);

-- Convert to hypertable
SELECT create_hypertable(
    'mutual_funds.benchmark_nav_history',
    'nav_date',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

-- Indexes
CREATE INDEX idx_benchmark_nav_history_code ON mutual_funds.benchmark_nav_history(benchmark_code, nav_date DESC);
CREATE INDEX idx_benchmark_nav_history_date ON mutual_funds.benchmark_nav_history(nav_date DESC);

-- Enable compression
ALTER TABLE mutual_funds.benchmark_nav_history SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'benchmark_code',
    timescaledb.compress_orderby = 'nav_date DESC'
);

SELECT add_compression_policy('mutual_funds.benchmark_nav_history', INTERVAL '90 days');

COMMENT ON TABLE mutual_funds.benchmark_nav_history IS 'TimescaleDB hypertable storing daily historical index values for benchmark indices';

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION mutual_funds.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER trg_fund_master_updated_at 
    BEFORE UPDATE ON mutual_funds.fund_master
    FOR EACH ROW 
    EXECUTE FUNCTION mutual_funds.update_updated_at_column();

CREATE TRIGGER trg_fund_metrics_updated_at 
    BEFORE UPDATE ON mutual_funds.fund_metrics
    FOR EACH ROW 
    EXECUTE FUNCTION mutual_funds.update_updated_at_column();

CREATE TRIGGER trg_benchmark_master_updated_at 
    BEFORE UPDATE ON mutual_funds.benchmark_master
    FOR EACH ROW 
    EXECUTE FUNCTION mutual_funds.update_updated_at_column();

-- ============================================================================
-- CONTINUOUS AGGREGATES
-- ============================================================================

-- Monthly NAV aggregates for funds
CREATE MATERIALIZED VIEW mutual_funds.fund_nav_monthly_stats
WITH (timescaledb.continuous) AS
SELECT 
    scheme_code,
    time_bucket('1 month', nav_date) AS month,
    FIRST(nav_value, nav_date) AS opening_nav,
    LAST(nav_value, nav_date) AS closing_nav,
    MAX(nav_value) AS highest_nav,
    MIN(nav_value) AS lowest_nav,
    AVG(nav_value) AS average_nav,
    COUNT(*) AS trading_days_count
FROM mutual_funds.fund_nav_history
GROUP BY scheme_code, month;

SELECT add_continuous_aggregate_policy('mutual_funds.fund_nav_monthly_stats',
    start_offset => INTERVAL '3 months',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');

CREATE INDEX idx_fund_nav_monthly_scheme ON mutual_funds.fund_nav_monthly_stats(scheme_code, month DESC);

-- Monthly benchmark aggregates
CREATE MATERIALIZED VIEW mutual_funds.benchmark_nav_monthly_stats
WITH (timescaledb.continuous) AS
SELECT 
    benchmark_code,
    time_bucket('1 month', nav_date) AS month,
    FIRST(index_value, nav_date) AS opening_value,
    LAST(index_value, nav_date) AS closing_value,
    MAX(index_value) AS highest_value,
    MIN(index_value) AS lowest_value,
    AVG(index_value) AS average_value,
    COUNT(*) AS trading_days_count
FROM mutual_funds.benchmark_nav_history
GROUP BY benchmark_code, month;

SELECT add_continuous_aggregate_policy('mutual_funds.benchmark_nav_monthly_stats',
    start_offset => INTERVAL '3 months',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');

CREATE INDEX idx_benchmark_nav_monthly_code ON mutual_funds.benchmark_nav_monthly_stats(benchmark_code, month DESC);

-- ============================================================================
-- MATERIALIZED VIEWS
-- ============================================================================

CREATE MATERIALIZED VIEW mutual_funds.mv_top_funds_by_category AS
SELECT 
    fm.scheme_code,
    fm.scheme_name,
    fm.amc_name,
    fm.scheme_category,
    fm.scheme_subcategory,
    fm.plan_type,
    fme.current_nav,
    fme.nav_date,
    fme.aum_in_crores,
    fme.rolling_return_3year,
    fme.rolling_return_5year,
    fme.sharpe_ratio,
    fme.sortino_ratio,
    fme.alpha,
    fme.beta,
    fme.standard_deviation,
    fme.maximum_drawdown
FROM mutual_funds.fund_master fm
INNER JOIN mutual_funds.fund_metrics fme ON fm.scheme_code = fme.scheme_code
WHERE fm.is_active = TRUE
ORDER BY fm.scheme_category, fme.rolling_return_3year DESC NULLS LAST;

CREATE UNIQUE INDEX idx_mv_top_funds_scheme ON mutual_funds.mv_top_funds_by_category(scheme_code);
CREATE INDEX idx_mv_top_funds_category ON mutual_funds.mv_top_funds_by_category(scheme_category, scheme_subcategory);

CREATE MATERIALIZED VIEW mutual_funds.mv_category_performance_stats AS
SELECT 
    fm.scheme_category,
    fm.scheme_subcategory,
    fm.plan_type,
    COUNT(*) as total_funds,
    COUNT(*) FILTER (WHERE fme.rolling_return_3year IS NOT NULL) as funds_with_3yr_data,
    AVG(fme.rolling_return_3year) as avg_3yr_return,
    AVG(fme.rolling_return_5year) as avg_5yr_return,
    AVG(fme.sharpe_ratio) as avg_sharpe_ratio,
    AVG(fme.sortino_ratio) as avg_sortino_ratio,
    AVG(fme.standard_deviation) as avg_std_deviation,
    AVG(fme.alpha) as avg_alpha,
    AVG(fme.beta) as avg_beta,
    SUM(fme.aum_in_crores) as total_aum_crores,
    MAX(fme.rolling_return_3year) as best_3yr_return,
    MIN(fme.rolling_return_3year) as worst_3yr_return,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fme.rolling_return_3year) as median_3yr_return,
    MAX(fme.nav_date) as data_as_of_date
FROM mutual_funds.fund_master fm
INNER JOIN mutual_funds.fund_metrics fme ON fm.scheme_code = fme.scheme_code
WHERE fm.is_active = TRUE
GROUP BY fm.scheme_category, fm.scheme_subcategory, fm.plan_type;

CREATE INDEX idx_mv_category_stats ON mutual_funds.mv_category_performance_stats(scheme_category, scheme_subcategory, plan_type);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION mutual_funds.refresh_all_analytics_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mutual_funds.mv_top_funds_by_category;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mutual_funds.mv_category_performance_stats;
    RAISE NOTICE 'All materialized views refreshed successfully';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA mutual_funds TO mf_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA mutual_funds TO mf_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA mutual_funds TO mf_admin;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA mutual_funds TO mf_admin;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Database initialization completed!';
    RAISE NOTICE 'Schema: mutual_funds';
    RAISE NOTICE 'Tables created: 5';
    RAISE NOTICE 'Hypertables: 2 (fund_nav_history, benchmark_nav_history)';
    RAISE NOTICE 'Continuous Aggregates: 2';
    RAISE NOTICE 'Materialized Views: 2';
    RAISE NOTICE '========================================';
END $$;