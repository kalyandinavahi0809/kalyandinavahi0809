-- Data Quality Queries for Network Signal Imputation
-- This file contains queries for monitoring data quality

-- ============================================================================
-- Missing Data Analysis
-- ============================================================================

-- Check missing data percentage by feature
SELECT
    'signal_strength' AS feature,
    COUNT(*) AS total_records,
    SUM(CASE WHEN signal_strength IS NULL THEN 1 ELSE 0 END) AS missing_count,
    ROUND(100.0 * SUM(CASE WHEN signal_strength IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS missing_percentage
FROM raw_signals
WHERE timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())

UNION ALL

SELECT
    'signal_quality' AS feature,
    COUNT(*) AS total_records,
    SUM(CASE WHEN signal_quality IS NULL THEN 1 ELSE 0 END) AS missing_count,
    ROUND(100.0 * SUM(CASE WHEN signal_quality IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS missing_percentage
FROM raw_signals
WHERE timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())

UNION ALL

SELECT
    'bandwidth_usage' AS feature,
    COUNT(*) AS total_records,
    SUM(CASE WHEN bandwidth_usage IS NULL THEN 1 ELSE 0 END) AS missing_count,
    ROUND(100.0 * SUM(CASE WHEN bandwidth_usage IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS missing_percentage
FROM raw_signals
WHERE timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP());

-- ============================================================================
-- Data Distribution Checks
-- ============================================================================

-- Check for outliers in signal strength
SELECT
    DATE_TRUNC('day', timestamp) AS day,
    MIN(signal_strength) AS min_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY signal_strength) AS q1,
    MEDIAN(signal_strength) AS median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY signal_strength) AS q3,
    MAX(signal_strength) AS max_value,
    AVG(signal_strength) AS mean,
    STDDEV(signal_strength) AS stddev
FROM raw_signals
WHERE timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    AND signal_strength IS NOT NULL
GROUP BY DATE_TRUNC('day', timestamp)
ORDER BY day DESC;

-- ============================================================================
-- Data Freshness Checks
-- ============================================================================

-- Check data freshness by signal source
SELECT
    signal_id,
    MAX(timestamp) AS last_signal_timestamp,
    DATEDIFF(minute, MAX(timestamp), CURRENT_TIMESTAMP()) AS minutes_since_last_signal,
    COUNT(*) AS total_signals_last_24h
FROM raw_signals
WHERE timestamp >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
GROUP BY signal_id
HAVING DATEDIFF(minute, MAX(timestamp), CURRENT_TIMESTAMP()) > 60
ORDER BY minutes_since_last_signal DESC;

-- ============================================================================
-- Data Consistency Checks
-- ============================================================================

-- Check for duplicate records
SELECT
    signal_id,
    timestamp,
    COUNT(*) AS duplicate_count
FROM raw_signals
WHERE timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY signal_id, timestamp
HAVING COUNT(*) > 1;

-- Check for invalid values
SELECT
    'signal_strength_out_of_range' AS check_type,
    COUNT(*) AS violation_count
FROM raw_signals
WHERE timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    AND signal_strength IS NOT NULL
    AND (signal_strength < -120 OR signal_strength > 0)

UNION ALL

SELECT
    'bandwidth_out_of_range' AS check_type,
    COUNT(*) AS violation_count
FROM raw_signals
WHERE timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    AND bandwidth_usage IS NOT NULL
    AND (bandwidth_usage < 0 OR bandwidth_usage > 100);

-- ============================================================================
-- Feature Correlation Analysis
-- ============================================================================

-- Calculate correlation between features
SELECT
    CORR(signal_strength, signal_quality) AS signal_strength_quality_corr,
    CORR(signal_strength, bandwidth_usage) AS signal_strength_bandwidth_corr,
    CORR(signal_quality, bandwidth_usage) AS signal_quality_bandwidth_corr
FROM raw_signals
WHERE timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())
    AND signal_strength IS NOT NULL
    AND signal_quality IS NOT NULL
    AND bandwidth_usage IS NOT NULL;

-- ============================================================================
-- Imputation Quality Checks
-- ============================================================================

-- Compare imputed values with ground truth (when available)
SELECT
    model_version,
    DATE_TRUNC('day', prediction_timestamp) AS day,
    COUNT(*) AS total_predictions,
    AVG(ABS(predicted_value - actual_value)) AS mae,
    SQRT(AVG(POWER(predicted_value - actual_value, 2))) AS rmse,
    MAX(ABS(predicted_value - actual_value)) AS max_error,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY ABS(predicted_value - actual_value)) AS p95_error
FROM model_predictions
WHERE actual_value IS NOT NULL
    AND prediction_timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY model_version, DATE_TRUNC('day', prediction_timestamp)
ORDER BY day DESC, model_version;

-- ============================================================================
-- Monitoring Dashboard Queries
-- ============================================================================

-- Daily summary for monitoring dashboard
SELECT
    DATE_TRUNC('day', timestamp) AS day,
    COUNT(*) AS total_records,
    COUNT(DISTINCT signal_id) AS unique_signals,
    AVG(signal_strength) AS avg_signal_strength,
    STDDEV(signal_strength) AS stddev_signal_strength,
    SUM(CASE WHEN signal_strength IS NULL THEN 1 ELSE 0 END) AS missing_count,
    ROUND(100.0 * SUM(CASE WHEN signal_strength IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS missing_percentage
FROM raw_signals
WHERE timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY DATE_TRUNC('day', timestamp)
ORDER BY day DESC;
