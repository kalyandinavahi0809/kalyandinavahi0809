# SQL

This directory contains SQL scripts for the Network Signal Imputation pipeline.

## Files

- **inference_table_function.sql**: Snowflake UDF for real-time inference
- **view_definitions.sql**: Feature engineering and monitoring views
- **quality_queries.sql**: Data quality monitoring queries

## Architecture

### Inference Layer
- Table functions for real-time predictions
- Batch scoring procedures
- Model serving endpoints

### Feature Store
- Feature engineering views
- Temporal feature aggregations
- Feature lineage tracking

### Monitoring
- Data quality metrics
- Model performance tracking
- Drift detection queries

## Usage

### Deploy Views

```sql
-- Execute in Snowflake
USE DATABASE ML_DATABASE;
USE SCHEMA ML_SCHEMA;

-- Create views
@view_definitions.sql

-- Create inference function
@inference_table_function.sql
```

### Run Quality Checks

```sql
-- Execute quality checks
@quality_queries.sql

-- Check missing data
SELECT * FROM VW_DATA_QUALITY_METRICS
WHERE day >= DATEADD(day, -7, CURRENT_TIMESTAMP());
```

### Inference Example

```sql
-- Real-time inference
SELECT * FROM TABLE(SIGNAL_IMPUTATION_INFERENCE(
    'SIGNAL_001',
    '2024-01-01 00:00:00'::TIMESTAMP_NTZ,
    OBJECT_CONSTRUCT(
        'signal_strength', -75,
        'bandwidth', 80,
        'network_type', '5G'
    )
));

-- Batch inference
SELECT
    s.signal_id,
    s.timestamp,
    i.imputed_value,
    i.confidence_score
FROM VW_SIGNALS_REQUIRING_IMPUTATION s
CROSS JOIN TABLE(SIGNAL_IMPUTATION_INFERENCE(
    s.signal_id,
    s.timestamp,
    OBJECT_CONSTRUCT(
        'signal_quality', s.signal_quality,
        'bandwidth_usage', s.bandwidth_usage,
        'network_type', s.network_type
    )
)) i;
```

## Permissions

Required roles and grants:
- `ML_DEVELOPER_ROLE`: Feature engineering access
- `ML_INFERENCE_ROLE`: Inference function execution
- `ML_MONITORING_ROLE`: Monitoring views access

## Best Practices

1. **Partitioning**: Use time-based partitioning for large tables
2. **Clustering**: Cluster on signal_id and timestamp
3. **Caching**: Enable result caching for repeated queries
4. **Monitoring**: Run quality checks daily
5. **Performance**: Use materialized views for expensive aggregations
