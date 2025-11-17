# Feature Store Guide

## Overview

The Feature Store is a centralized repository for managing features in the Network Signal Imputation ML pipeline. It provides consistent feature definitions, transformations, and serving capabilities for both training and inference.

## Why Feature Store?

### Benefits
- **Consistency**: Same features for training and inference
- **Reusability**: Share features across multiple models
- **Versioning**: Track feature changes over time
- **Performance**: Optimized feature retrieval
- **Monitoring**: Track feature quality and drift

### Problems It Solves
- Training/serving skew
- Feature engineering duplication
- Lack of feature documentation
- Difficulty in feature discovery
- Inconsistent feature transformations

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Raw Data Sources                    │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────▼─────────┐
         │  Feature Pipeline │
         │  - Transformations│
         │  - Aggregations   │
         │  - Validations    │
         └─────────┬─────────┘
                   │
    ┌──────────────┴──────────────┐
    │                             │
┌───▼────────────┐    ┌───────────▼──────────┐
│ Offline Store  │    │   Online Store       │
│ (Training)     │    │   (Inference)        │
│ - Historical   │    │   - Latest values    │
│ - Full dataset │    │   - Low latency      │
└───┬────────────┘    └───────────┬──────────┘
    │                             │
    │                             │
┌───▼────────────┐    ┌───────────▼──────────┐
│  Model         │    │   Real-time          │
│  Training      │    │   Inference          │
└────────────────┘    └──────────────────────┘
```

## Feature Definitions

### Feature Schema

Each feature has:
- **Name**: Unique identifier
- **Type**: Numerical, categorical, or timestamp
- **Description**: What the feature represents
- **Source**: Origin table and column
- **Transformation**: Applied transformation logic
- **Required**: Whether feature is mandatory

### Example Feature Definition

```python
from feature_store.feature_definitions import FeatureDefinition, FeatureType

signal_strength_feature = FeatureDefinition(
    name="signal_strength",
    feature_type=FeatureType.NUMERICAL,
    description="Network signal strength in dBm",
    source_table="raw_signals",
    source_column="strength",
    transformation="standardize",
    is_required=True
)
```

## Available Features

### Signal Features

#### signal_strength
- **Type**: Numerical
- **Range**: -120 to 0 dBm
- **Transformation**: Standardization (z-score)
- **Description**: Strength of network signal

#### signal_quality
- **Type**: Numerical
- **Range**: 0 to 100
- **Transformation**: Min-max normalization
- **Description**: Quality indicator of signal

#### bandwidth_usage
- **Type**: Numerical
- **Range**: 0 to 100 (percentage)
- **Transformation**: Standardization
- **Description**: Percentage of bandwidth utilized

#### network_type
- **Type**: Categorical
- **Values**: 4G, 5G, LTE, 3G
- **Transformation**: One-hot encoding
- **Description**: Type of network connection

### Temporal Features

#### hour_of_day
- **Type**: Categorical (0-23)
- **Transformation**: Cyclical encoding (sin/cos)
- **Description**: Hour when signal was measured

#### day_of_week
- **Type**: Categorical (0-6)
- **Transformation**: One-hot encoding
- **Description**: Day of week for temporal patterns

### Aggregated Features

#### avg_signal_strength_1h
- **Description**: Average signal strength over last hour
- **Window**: 1 hour
- **Aggregation**: Mean

#### stddev_signal_strength_1h
- **Description**: Standard deviation of signal strength over last hour
- **Window**: 1 hour
- **Aggregation**: Standard deviation

### Lag Features

#### signal_strength_lag_1
- **Description**: Signal strength from 1 hour ago
- **Lag**: 1 hour

#### signal_strength_lag_24
- **Description**: Signal strength from 24 hours ago
- **Lag**: 24 hours

## Setup and Initialization

### Prerequisites
```bash
# Install required packages
pip install snowflake-connector-python pandas numpy
```

### Configuration

```python
config = {
    "warehouse": "COMPUTE_WH",
    "database": "ML_DATABASE",
    "schema": "FEATURE_STORE",
    "role": "ML_DEVELOPER_ROLE"
}
```

### Initialize Feature Store

```python
from feature_store.setup_feature_store import FeatureStoreSetup

# Create setup instance
setup = FeatureStoreSetup(config)

# Initialize feature store
setup.initialize()
```

This will:
1. Connect to Snowflake
2. Create feature groups
3. Setup materialization pipelines
4. Validate feature definitions

## Feature Engineering

### Adding New Features

1. **Define Feature**

```python
from feature_store.feature_definitions import FeatureDefinition, FeatureType

new_feature = FeatureDefinition(
    name="latency_metric",
    feature_type=FeatureType.NUMERICAL,
    description="Network latency in milliseconds",
    source_table="raw_signals",
    source_column="latency",
    transformation="log_transform",
    is_required=False
)
```

2. **Add to Feature List**

```python
# In feature_definitions.py
SIGNAL_FEATURES.append(new_feature)
```

3. **Update Feature Store**

```python
setup = FeatureStoreSetup(config)
setup.create_feature_groups()
```

### Feature Transformations

#### Standardization (Z-score)
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
standardized = scaler.fit_transform(data[['signal_strength']])
```

#### Normalization (Min-Max)
```python
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
normalized = scaler.fit_transform(data[['signal_quality']])
```

#### One-Hot Encoding
```python
import pandas as pd

encoded = pd.get_dummies(data['network_type'], prefix='network')
```

#### Log Transform
```python
import numpy as np

log_transformed = np.log1p(data['bandwidth_usage'])
```

## Retrieving Features

### For Training

```python
from feature_store.feature_definitions import get_feature_names

# Get all feature names
feature_names = get_feature_names()

# Query from feature store
query = f"""
SELECT 
    signal_id,
    timestamp,
    {', '.join(feature_names)}
FROM FEATURE_STORE.VW_TRAINING_FEATURES
WHERE timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())
"""

# Execute query and load into DataFrame
features_df = pd.read_sql(query, connection)
```

### For Inference

```python
# Real-time feature retrieval
def get_features_for_inference(signal_id, timestamp):
    query = f"""
    SELECT 
        signal_strength,
        signal_quality,
        bandwidth_usage,
        network_type
    FROM FEATURE_STORE.VW_LATEST_FEATURES
    WHERE signal_id = '{signal_id}'
        AND timestamp = '{timestamp}'
    """
    
    return pd.read_sql(query, connection)
```

## Feature Validation

### Data Quality Checks

```python
def validate_features(df):
    """Validate feature data quality."""
    
    # Check for missing values
    missing_pct = df.isna().mean() * 100
    assert missing_pct.max() < 30, "Too many missing values"
    
    # Check value ranges
    assert df['signal_strength'].between(-120, 0).all()
    assert df['signal_quality'].between(0, 100).all()
    assert df['bandwidth_usage'].between(0, 100).all()
    
    # Check for duplicates
    duplicates = df.duplicated(subset=['signal_id', 'timestamp'])
    assert duplicates.sum() == 0, "Duplicate records found"
    
    return True
```

## Feature Monitoring

### Drift Detection

```python
from monitoring.drift_detection import DriftDetector

# Initialize drift detector
detector = DriftDetector(config)

# Set reference data (baseline)
detector.set_reference_data(reference_df)

# Check for drift
drift_results = detector.detect_feature_drift(current_df)

# Review results
for feature, result in drift_results.items():
    if result['drift_detected']:
        print(f"Drift detected in {feature}: PSI = {result['psi']:.4f}")
```

### Feature Statistics

```sql
-- Monitor feature statistics
SELECT
    DATE_TRUNC('day', timestamp) AS day,
    AVG(signal_strength) AS avg_signal,
    STDDEV(signal_strength) AS std_signal,
    MIN(signal_strength) AS min_signal,
    MAX(signal_strength) AS max_signal,
    COUNT(*) AS record_count
FROM FEATURE_STORE.VW_TRAINING_FEATURES
GROUP BY DATE_TRUNC('day', timestamp)
ORDER BY day DESC
LIMIT 30;
```

## Best Practices

### Feature Naming
- Use descriptive, lowercase names
- Use underscores for word separation
- Include aggregation window in name (e.g., `avg_1h`)
- Prefix transformed features (e.g., `log_bandwidth`)

### Feature Documentation
- Always provide clear descriptions
- Document valid value ranges
- Specify transformation logic
- Include example values

### Feature Versioning
- Version features when schema changes
- Track feature lineage
- Maintain backward compatibility
- Document breaking changes

### Performance Optimization
- Materialize expensive features
- Use appropriate data types
- Partition by time for large datasets
- Cache frequently used features

### Testing Features
```python
def test_feature_schema():
    """Test feature schema is valid."""
    from feature_store.feature_definitions import SIGNAL_FEATURES
    
    for feature in SIGNAL_FEATURES:
        assert feature.name
        assert feature.description
        assert feature.source_table
        assert feature.source_column
```

## Troubleshooting

### Issue: Missing Features
```python
# Check if feature exists
from feature_store.feature_definitions import get_feature_names

feature_names = get_feature_names()
assert 'signal_strength' in feature_names
```

### Issue: Feature Values Out of Range
```python
# Add validation in feature pipeline
def validate_signal_strength(value):
    if value < -120 or value > 0:
        raise ValueError(f"Signal strength {value} out of valid range")
    return value
```

### Issue: Slow Feature Retrieval
```sql
-- Add clustering for better performance
ALTER TABLE FEATURE_STORE.FEATURES 
CLUSTER BY (signal_id, timestamp);

-- Create materialized view
CREATE MATERIALIZED VIEW FEATURE_STORE.MV_LATEST_FEATURES AS
SELECT * FROM FEATURE_STORE.VW_LATEST_FEATURES;
```

## Integration with ML Pipeline

### Training Integration

```python
from modeling.pipeline import SignalImputationPipeline

# Configure to use feature store
config = {
    "feature_store": "enabled",
    "feature_store_schema": "FEATURE_STORE"
}

pipeline = SignalImputationPipeline(config)
pipeline.run()
```

### Inference Integration

```sql
-- Use features in inference function
CREATE OR REPLACE FUNCTION SIGNAL_IMPUTATION_INFERENCE(...)
AS
$$
    # Get features from feature store
    features = get_features(signal_id, timestamp)
    
    # Make prediction
    prediction = model.predict(features)
    
    return prediction
$$;
```

## Advanced Topics

### Feature Store as a Service
- REST API for feature access
- gRPC for high-performance serving
- Feature store SDK

### Online-Offline Consistency
- Ensure same transformations
- Validate feature parity
- Monitor serving latency

### Feature Discovery
- Feature catalog
- Feature lineage visualization
- Feature usage tracking

## Resources

- [Feature Store Documentation](#)
- [Snowflake Feature Store](#)
- [Feature Engineering Best Practices](#)
- [MLOps Guide](#)

## Support

For questions or issues with the feature store:
- **Slack**: #ml-feature-store
- **Email**: ml-team@company.com
- **Documentation**: Internal wiki
