# Feature Store

This directory contains feature store setup and feature definitions for the Network Signal Imputation pipeline.

## Files

- **setup_feature_store.py**: Initializes and configures the feature store
- **feature_definitions.py**: Defines all features used in the ML pipeline

## Feature Store Architecture

The feature store acts as a centralized repository for feature engineering, providing:
- Consistent feature definitions across training and inference
- Feature versioning and lineage
- Feature freshness and quality monitoring
- Efficient feature serving

## Usage

### Initialize Feature Store

```python
from feature_store.setup_feature_store import FeatureStoreSetup

config = {
    "warehouse": "COMPUTE_WH",
    "database": "ML_DATABASE",
    "schema": "FEATURE_STORE"
}

setup = FeatureStoreSetup(config)
setup.initialize()
```

### Access Feature Definitions

```python
from feature_store.feature_definitions import SIGNAL_FEATURES, get_feature_names

# Get all feature names
feature_names = get_feature_names()

# Access individual feature definitions
for feature in SIGNAL_FEATURES:
    print(f"{feature.name}: {feature.description}")
```

## Integration

The feature store integrates with:
- Snowflake Feature Store
- Model training pipeline
- Real-time inference endpoints
