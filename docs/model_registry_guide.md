# Model Registry Guide

## Overview

The Model Registry is a centralized system for versioning, storing, and managing machine learning models in the Network Signal Imputation pipeline. It provides model lifecycle management, metadata tracking, and deployment controls.

## Why Model Registry?

### Benefits
- **Version Control**: Track all model versions with metadata
- **Reproducibility**: Reproduce model training and results
- **Governance**: Control model promotion and deployment
- **Lineage**: Track model ancestry and dependencies
- **Collaboration**: Share models across teams

### Problems It Solves
- Model versioning chaos
- Lack of model metadata
- Difficult rollbacks
- No deployment controls
- Lost model artifacts

## Architecture

```
┌────────────────────────────────────────────────────┐
│              Model Development                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Training │→ │Validation│→ │ Testing  │        │
│  └──────────┘  └──────────┘  └──────────┘        │
└──────────────────┬─────────────────────────────────┘
                   │
           ┌───────▼────────┐
           │ Model Registry │
           │  - Versions    │
           │  - Metadata    │
           │  - Artifacts   │
           └───────┬────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐    ┌────▼─────┐   ┌──▼──────┐
│  Dev   │    │ Staging  │   │  Prod   │
│ Stage  │    │  Stage   │   │ Stage   │
└────────┘    └──────────┘   └─────────┘
```

## Model Lifecycle Stages

### 1. Development
- **Purpose**: Experimental models
- **Access**: All ML developers
- **Validation**: Basic tests
- **Deployment**: Not deployed

### 2. Staging
- **Purpose**: Pre-production validation
- **Access**: ML engineers
- **Validation**: Comprehensive tests
- **Deployment**: Staging environment

### 3. Production
- **Purpose**: Serving live predictions
- **Access**: Automated systems
- **Validation**: Production-ready
- **Deployment**: Production environment

### 4. Archived
- **Purpose**: Deprecated models
- **Access**: Read-only
- **Validation**: N/A
- **Deployment**: Not deployed

## Setup and Configuration

### Installation

```bash
pip install snowflake-connector-python mlflow boto3
```

### Configuration

```python
from modeling.registry import ModelRegistry

# Initialize registry
registry = ModelRegistry(
    registry_uri="snowflake://models",
    warehouse="COMPUTE_WH",
    database="ML_DATABASE",
    schema="MODEL_REGISTRY"
)

# Connect
registry.connect()
```

### Environment Variables

```bash
export MODEL_REGISTRY_URI="snowflake://models"
export MODEL_STORAGE_PATH="s3://ml-models/signal-imputation/"
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
```

## Registering Models

### Basic Registration

```python
from modeling.registry import ModelRegistry

registry = ModelRegistry("snowflake://models")
registry.connect()

# Register model
version = registry.register_model(
    model_name="signal_imputation_v1",
    model_path="models/xgboost_model.pkl",
    metrics={
        "rmse": 0.15,
        "mae": 0.10,
        "r2": 0.95
    },
    metadata={
        "framework": "xgboost",
        "features": ["signal_strength", "bandwidth_usage"],
        "training_date": "2024-01-15",
        "dataset_size": 100000
    }
)

print(f"Model registered with version: {version}")
```

### Advanced Registration

```python
# Register with full metadata
version = registry.register_model(
    model_name="signal_imputation_v2",
    model_path="models/ensemble_model.pkl",
    metrics={
        "rmse": 0.12,
        "mae": 0.08,
        "r2": 0.97,
        "inference_time_ms": 45
    },
    metadata={
        "framework": "ensemble",
        "base_models": ["xgboost", "random_forest"],
        "hyperparameters": {
            "xgb_learning_rate": 0.1,
            "xgb_max_depth": 6,
            "rf_n_estimators": 100
        },
        "features": get_feature_names(),
        "training_duration_minutes": 25,
        "training_samples": 150000,
        "validation_samples": 30000,
        "test_samples": 20000,
        "git_commit": "a1b2c3d4",
        "author": "ml-team@company.com"
    }
)
```

## Model Promotion

### Promote to Staging

```python
from modeling.registry import ModelRegistry, ModelStage

registry = ModelRegistry("snowflake://models")

# Promote to staging
registry.promote_model(
    model_name="signal_imputation_v2",
    version="20240115_143022",
    stage=ModelStage.STAGING
)
```

### Promote to Production

```python
# Additional validation before production
validation_results = run_validation_tests(model, test_data)

if validation_results["all_passed"]:
    registry.promote_model(
        model_name="signal_imputation_v2",
        version="20240115_143022",
        stage=ModelStage.PRODUCTION
    )
    print("Model promoted to production")
else:
    print(f"Validation failed: {validation_results['failures']}")
```

### Approval Workflow

```python
def promote_with_approval(model_name, version, stage):
    """Promote model with approval process."""
    
    # Request approval
    approval_id = request_approval(
        model_name=model_name,
        version=version,
        target_stage=stage,
        approvers=["ml-lead@company.com", "product-owner@company.com"]
    )
    
    # Wait for approval
    if wait_for_approval(approval_id, timeout_hours=24):
        registry.promote_model(model_name, version, stage)
        notify_promotion_success(model_name, version, stage)
    else:
        notify_promotion_rejected(model_name, version, stage)
```

## Retrieving Models

### Get Production Model

```python
# Get latest production model
model = registry.get_model(
    model_name="signal_imputation_v2",
    stage=ModelStage.PRODUCTION
)

# Use model for inference
predictions = model.predict(features)
```

### Get Specific Version

```python
# Get specific model version
model = registry.get_model(
    model_name="signal_imputation_v2",
    version="20240115_143022"
)
```

### List All Models

```python
# List all registered models
models = registry.list_models()

for model_info in models:
    print(f"Name: {model_info['name']}")
    print(f"Version: {model_info['version']}")
    print(f"Stage: {model_info['stage']}")
    print(f"Metrics: {model_info['metrics']}")
    print("---")
```

## Model Metadata

### Required Metadata

```python
required_metadata = {
    "framework": "xgboost",  # ML framework used
    "training_date": "2024-01-15",  # When model was trained
    "features": ["signal_strength", "..."],  # Input features
    "target": "signal_strength",  # Target variable
    "git_commit": "a1b2c3d4"  # Git commit hash
}
```

### Recommended Metadata

```python
recommended_metadata = {
    "author": "ml-team@company.com",
    "description": "XGBoost model for signal imputation",
    "hyperparameters": {...},
    "training_duration_minutes": 25,
    "dataset_size": 100000,
    "feature_importance": {...},
    "cross_validation_scores": [...],
    "preprocessing_steps": [...]
}
```

## Model Versioning

### Version Format

Versions follow the format: `YYYYMMDD_HHMMSS`

Example: `20240115_143022` (January 15, 2024 at 14:30:22)

### Semantic Versioning

For major changes, use tags:
- `v1.0.0`: Initial production model
- `v1.1.0`: Minor improvements
- `v2.0.0`: Major architecture change

```python
# Add semantic version tag
registry.tag_version(
    model_name="signal_imputation_v2",
    version="20240115_143022",
    tag="v2.0.0"
)
```

## Model Comparison

### Compare Metrics

```python
def compare_models(model1_version, model2_version):
    """Compare two model versions."""
    
    # Get models
    model1 = registry.get_model_metadata("signal_imputation_v2", model1_version)
    model2 = registry.get_model_metadata("signal_imputation_v2", model2_version)
    
    # Compare metrics
    comparison = {
        "rmse_diff": model2["metrics"]["rmse"] - model1["metrics"]["rmse"],
        "mae_diff": model2["metrics"]["mae"] - model1["metrics"]["mae"],
        "r2_diff": model2["metrics"]["r2"] - model1["metrics"]["r2"]
    }
    
    return comparison

# Usage
comparison = compare_models("20240110_120000", "20240115_143022")
print(f"RMSE improvement: {-comparison['rmse_diff']:.4f}")
```

### A/B Testing

```python
def setup_ab_test(control_version, treatment_version, traffic_split=0.5):
    """Setup A/B test between two model versions."""
    
    ab_config = {
        "test_name": "signal_imputation_ab_test",
        "control": {
            "version": control_version,
            "traffic_percentage": traffic_split * 100
        },
        "treatment": {
            "version": treatment_version,
            "traffic_percentage": (1 - traffic_split) * 100
        },
        "metrics": ["rmse", "mae", "latency_ms"],
        "duration_days": 7
    }
    
    return deploy_ab_test(ab_config)
```

## Model Archiving

### Archive Old Model

```python
# Archive deprecated model
registry.archive_model(
    model_name="signal_imputation_v1",
    version="20231201_100000"
)

print("Model archived. No longer available for deployment.")
```

### Retention Policy

```python
def cleanup_old_models(days_to_keep=90):
    """Archive models older than specified days."""
    
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    models = registry.list_models()
    
    for model in models:
        if model['stage'] == 'development':
            version_date = datetime.strptime(model['version'], '%Y%m%d_%H%M%S')
            
            if version_date < cutoff_date:
                registry.archive_model(model['name'], model['version'])
                print(f"Archived {model['name']} version {model['version']}")
```

## Integration with ML Pipeline

### Automated Registration

```python
from modeling.pipeline import SignalImputationPipeline
from modeling.registry import ModelRegistry

# Train model
pipeline = SignalImputationPipeline(config)
pipeline.run()

# Automatically register if metrics meet threshold
if pipeline.metrics['rmse'] < 0.20:
    registry = ModelRegistry("snowflake://models")
    version = registry.register_model(
        model_name="signal_imputation_v2",
        model_path=pipeline.model_path,
        metrics=pipeline.metrics,
        metadata=pipeline.get_metadata()
    )
    print(f"Model auto-registered: {version}")
```

### CI/CD Integration

```yaml
# .github/workflows/retrain_model.yml
- name: Train and Register Model
  run: |
    python modeling/pipeline.py --mode train
    
    # Register if training successful
    if [ $? -eq 0 ]; then
      python scripts/register_model.py \
        --model-path models/latest \
        --metrics-file metrics.json
    fi
```

## Model Monitoring

### Track Model Performance

```sql
-- Query model performance over time
SELECT
    model_version,
    DATE_TRUNC('day', prediction_timestamp) AS day,
    AVG(ABS(predicted_value - actual_value)) AS mae,
    SQRT(AVG(POWER(predicted_value - actual_value, 2))) AS rmse,
    COUNT(*) AS prediction_count
FROM model_predictions
WHERE model_name = 'signal_imputation_v2'
    AND actual_value IS NOT NULL
    AND prediction_timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY model_version, day
ORDER BY day DESC, model_version;
```

### Alert on Performance Degradation

```python
def monitor_model_performance(model_name, threshold_rmse=0.25):
    """Monitor model performance and alert if degraded."""
    
    current_metrics = get_current_metrics(model_name)
    
    if current_metrics['rmse'] > threshold_rmse:
        send_alert(
            severity="critical",
            message=f"Model {model_name} RMSE {current_metrics['rmse']:.4f} exceeds threshold {threshold_rmse}"
        )
        
        # Trigger retraining
        trigger_retraining_workflow(model_name)
```

## Best Practices

### 1. Always Include Comprehensive Metadata
```python
# Good
metadata = {
    "framework": "xgboost",
    "features": get_feature_names(),
    "hyperparameters": model.get_params(),
    "git_commit": get_git_commit(),
    "training_duration": training_time,
    "author": "ml-team@company.com"
}

# Bad
metadata = {"framework": "xgboost"}
```

### 2. Test Before Promotion
```python
def test_before_promotion(model, version):
    """Run tests before promoting model."""
    
    tests = [
        test_inference_latency,
        test_prediction_quality,
        test_edge_cases,
        test_data_validation
    ]
    
    for test in tests:
        result = test(model)
        if not result.passed:
            raise ValueError(f"Test {test.__name__} failed: {result.message}")
    
    # All tests passed, safe to promote
    return True
```

### 3. Maintain Model Lineage
```python
# Track which model this is based on
metadata = {
    "parent_model": "signal_imputation_v1",
    "parent_version": "20240101_120000",
    "changes": "Added ensemble methods",
    "improvement": "RMSE reduced by 15%"
}
```

### 4. Document Model Limitations
```python
metadata = {
    "limitations": [
        "Not suitable for signal strength > -30 dBm",
        "Requires at least 3 recent measurements",
        "Performance degrades with >50% missing data"
    ],
    "known_issues": [
        "Slight bias for 5G networks",
        "Higher error during peak hours"
    ]
}
```

## Troubleshooting

### Issue: Model Not Found
```python
# Check if model exists
models = registry.list_models()
if "signal_imputation_v2" not in [m['name'] for m in models]:
    print("Model not registered. Register first.")
```

### Issue: Cannot Promote to Production
```python
# Check current stage
model_info = registry.get_model_info("signal_imputation_v2", version)
print(f"Current stage: {model_info['stage']}")

# Must go through staging first
if model_info['stage'] != ModelStage.STAGING:
    print("Model must be in staging before production promotion")
```

### Issue: Model Artifacts Missing
```python
# Verify artifacts exist
import os

if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model artifacts not found at {model_path}")
    
# Check artifact integrity
verify_model_integrity(model_path)
```

## Resources

- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
- [Snowflake ML Model Management](#)
- [Model Governance Best Practices](#)
- [MLOps Guidelines](#)

## Support

For questions about the model registry:
- **Slack**: #ml-model-registry
- **Email**: ml-team@company.com
- **Documentation**: [Internal Wiki](#)
