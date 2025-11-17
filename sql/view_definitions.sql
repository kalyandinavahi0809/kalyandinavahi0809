-- View Definitions for Network Signal Imputation Pipeline
-- This file contains all view definitions for the ML pipeline

-- ============================================================================
-- Feature Engineering Views
-- ============================================================================

-- Raw signals with basic transformations
CREATE OR REPLACE VIEW VW_RAW_SIGNALS AS
SELECT
    signal_id,
    timestamp,
    signal_strength,
    signal_quality,
    bandwidth_usage,
    network_type,
    location_id,
    device_type
FROM raw_signals
WHERE timestamp >= DATEADD(day, -90, CURRENT_TIMESTAMP());

-- Aggregated signal features
CREATE OR REPLACE VIEW VW_SIGNAL_FEATURES_AGG AS
SELECT
    signal_id,
    DATE_TRUNC('hour', timestamp) AS hour,
    AVG(signal_strength) AS avg_signal_strength,
    STDDEV(signal_strength) AS stddev_signal_strength,
    MIN(signal_strength) AS min_signal_strength,
    MAX(signal_strength) AS max_signal_strength,
    AVG(bandwidth_usage) AS avg_bandwidth,
    COUNT(*) AS sample_count,
    SUM(CASE WHEN signal_strength IS NULL THEN 1 ELSE 0 END) AS missing_count
FROM VW_RAW_SIGNALS
GROUP BY signal_id, DATE_TRUNC('hour', timestamp);

-- Feature store view for training
CREATE OR REPLACE VIEW VW_TRAINING_FEATURES AS
SELECT
    r.signal_id,
    r.timestamp,
    r.signal_strength AS target,
    r.signal_quality,
    r.bandwidth_usage,
    r.network_type,
    a.avg_signal_strength,
    a.stddev_signal_strength,
    LAG(r.signal_strength, 1) OVER (PARTITION BY r.signal_id ORDER BY r.timestamp) AS prev_signal,
    LEAD(r.signal_strength, 1) OVER (PARTITION BY r.signal_id ORDER BY r.timestamp) AS next_signal,
    DATEDIFF(minute, LAG(r.timestamp) OVER (PARTITION BY r.signal_id ORDER BY r.timestamp), r.timestamp) AS time_gap
FROM VW_RAW_SIGNALS r
LEFT JOIN VW_SIGNAL_FEATURES_AGG a
    ON r.signal_id = a.signal_id
    AND DATE_TRUNC('hour', r.timestamp) = a.hour;

-- ============================================================================
-- Inference Views
-- ============================================================================

-- Latest signals requiring imputation
CREATE OR REPLACE VIEW VW_SIGNALS_REQUIRING_IMPUTATION AS
SELECT
    signal_id,
    timestamp,
    signal_quality,
    bandwidth_usage,
    network_type
FROM VW_RAW_SIGNALS
WHERE signal_strength IS NULL
    AND timestamp >= DATEADD(hour, -24, CURRENT_TIMESTAMP());

-- ============================================================================
-- Monitoring Views
-- ============================================================================

-- Model performance metrics over time
CREATE OR REPLACE VIEW VW_MODEL_PERFORMANCE_METRICS AS
SELECT
    model_version,
    DATE_TRUNC('day', prediction_timestamp) AS day,
    AVG(ABS(predicted_value - actual_value)) AS mae,
    SQRT(AVG(POWER(predicted_value - actual_value, 2))) AS rmse,
    CORR(predicted_value, actual_value) AS correlation,
    COUNT(*) AS prediction_count
FROM model_predictions
WHERE actual_value IS NOT NULL
GROUP BY model_version, DATE_TRUNC('day', prediction_timestamp);

-- Data quality metrics
CREATE OR REPLACE VIEW VW_DATA_QUALITY_METRICS AS
SELECT
    DATE_TRUNC('day', timestamp) AS day,
    COUNT(*) AS total_signals,
    SUM(CASE WHEN signal_strength IS NULL THEN 1 ELSE 0 END) AS missing_signal_strength,
    SUM(CASE WHEN signal_quality IS NULL THEN 1 ELSE 0 END) AS missing_signal_quality,
    SUM(CASE WHEN bandwidth_usage IS NULL THEN 1 ELSE 0 END) AS missing_bandwidth,
    AVG(signal_strength) AS avg_signal_strength,
    STDDEV(signal_strength) AS stddev_signal_strength
FROM VW_RAW_SIGNALS
GROUP BY DATE_TRUNC('day', timestamp);

-- Grant permissions on views
GRANT SELECT ON VW_RAW_SIGNALS TO ROLE ML_DEVELOPER_ROLE;
GRANT SELECT ON VW_SIGNAL_FEATURES_AGG TO ROLE ML_DEVELOPER_ROLE;
GRANT SELECT ON VW_TRAINING_FEATURES TO ROLE ML_DEVELOPER_ROLE;
GRANT SELECT ON VW_SIGNALS_REQUIRING_IMPUTATION TO ROLE ML_INFERENCE_ROLE;
GRANT SELECT ON VW_MODEL_PERFORMANCE_METRICS TO ROLE ML_MONITORING_ROLE;
GRANT SELECT ON VW_DATA_QUALITY_METRICS TO ROLE ML_MONITORING_ROLE;
