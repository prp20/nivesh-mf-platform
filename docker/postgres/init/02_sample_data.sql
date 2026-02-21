-- ============================================================================
-- SAMPLE DATA FOR TESTING
-- ============================================================================

SET search_path TO mutual_funds;

-- Insert sample benchmarks
INSERT INTO benchmark_master (benchmark_code, benchmark_name, benchmark_type, asset_class, is_active) VALUES
('NIFTY50', 'Nifty 50', 'Large Cap Equity', 'Equity', TRUE),
('NIFTY500', 'Nifty 500', 'Multi Cap Equity', 'Equity', TRUE),
('NIFTYMID150', 'Nifty Midcap 150', 'Mid Cap Equity', 'Equity', TRUE),
('CRISIL_LIQUID', 'CRISIL Liquid Fund Index', 'Liquid', 'Debt', TRUE);

-- Insert sample funds
INSERT INTO fund_master (scheme_code, scheme_name, amc_name, inception_date, plan_type, scheme_category, scheme_subcategory, benchmark_index_code, is_active) VALUES
('MF001-D', 'ABC Large Cap Fund - Direct Plan', 'ABC Asset Management', '2015-01-01', 'Direct', 'Equity Scheme', 'Large Cap Fund', 'NIFTY50', TRUE),
('MF001-R', 'ABC Large Cap Fund - Regular Plan', 'ABC Asset Management', '2015-01-01', 'Regular', 'Equity Scheme', 'Large Cap Fund', 'NIFTY50', TRUE),
('MF002-D', 'XYZ Mid Cap Fund - Direct Plan', 'XYZ Mutual Fund', '2016-06-15', 'Direct', 'Equity Scheme', 'Mid Cap Fund', 'NIFTYMID150', TRUE),
('MF003-D', 'DEF Liquid Fund - Direct Plan', 'DEF Asset Management', '2018-03-20', 'Direct', 'Debt Scheme', 'Liquid Fund', 'CRISIL_LIQUID', TRUE);

-- Insert sample benchmark historical data
INSERT INTO benchmark_nav_history (benchmark_code, nav_date, index_value)
SELECT 
    'NIFTY50',
    date_series,
    15000 + (RANDOM() * 2000 - 1000) -- Simulating index values between 14000-16000
FROM generate_series(
    '2023-01-01'::date,
    CURRENT_DATE,
    '1 day'::interval
) AS date_series
WHERE EXTRACT(DOW FROM date_series) BETWEEN 1 AND 5; -- Only weekdays

-- Insert sample NAV history for funds
INSERT INTO fund_nav_history (scheme_code, nav_date, nav_value)
SELECT 
    'MF001-D',
    date_series,
    50 + (RANDOM() * 10) -- NAV values between 50-60
FROM generate_series(
    '2023-01-01'::date,
    CURRENT_DATE,
    '1 day'::interval
) AS date_series
WHERE EXTRACT(DOW FROM date_series) BETWEEN 1 AND 5;

-- Insert sample metrics (you would calculate these in your application)
INSERT INTO fund_metrics (
    scheme_code, current_nav, nav_date, aum_in_crores,
    rolling_return_3year, rolling_return_5year,
    sharpe_ratio, sortino_ratio, alpha, beta, standard_deviation,
    maximum_drawdown, tracking_error, information_ratio,
    metrics_calculated_at, has_sufficient_data, data_completeness_percentage
) VALUES
('MF001-D', 58.45, CURRENT_DATE, 15000.50, 12.5, 14.8, 1.35, 1.52, 2.3, 0.98, 15.2, -8.5, 2.1, 0.45, CURRENT_TIMESTAMP, TRUE, 100.00),
('MF001-R', 56.20, CURRENT_DATE, 8500.25, 11.8, 14.1, 1.28, 1.45, 2.1, 0.98, 15.3, -8.7, 2.2, 0.42, CURRENT_TIMESTAMP, TRUE, 100.00),
('MF002-D', 42.30, CURRENT_DATE, 5200.75, 15.2, 16.5, 1.15, 1.38, 3.2, 1.15, 18.5, -12.3, 3.5, 0.38, CURRENT_TIMESTAMP, TRUE, 98.50),
('MF003-D', 1025.65, CURRENT_DATE, 25000.00, 6.5, 6.8, 2.10, 2.25, 0.5, 0.05, 0.8, -0.5, 0.2, 0.85, CURRENT_TIMESTAMP, TRUE, 100.00);

RAISE NOTICE 'Sample data inserted successfully!';