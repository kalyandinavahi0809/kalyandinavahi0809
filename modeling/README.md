# Modeling

This directory contains the ML modeling components for Network Signal Imputation.

## Files

- **pipeline.py**: End-to-end ML pipeline orchestration
- **registry.py**: Model versioning and lifecycle management
- **agent_model.py**: Intelligent agent-based imputation model
- **hyperparameter_tuning.py**: Automated hyperparameter optimization

## Pipeline Architecture

The modeling pipeline follows these stages:

1. **Data Loading**: Load data from feature store
2. **Preprocessing**: Clean and transform features
3. **Training**: Train imputation models
4. **Evaluation**: Validate model performance
5. **Registration**: Register model in registry

## Usage

### Run Complete Pipeline

```python
from modeling.pipeline import SignalImputationPipeline

config = {
    "data_source": "feature_store",
    "model_type": "xgboost",
    "feature_store": "enabled"
}

pipeline = SignalImputationPipeline(config)
pipeline.run()
```

### Hyperparameter Tuning

```python
from modeling.hyperparameter_tuning import HyperparameterTuner

config = {
    "search_method": "bayesian",
    "n_trials": 50
}

tuner = HyperparameterTuner(config)
best_params = tuner.tune(
    model_type="xgboost",
    train_fn=train_function,
    X_train=X_train,
    y_train=y_train,
    X_val=X_val,
    y_val=y_val
)
```

### Model Registry

```python
from modeling.registry import ModelRegistry, ModelStage

registry = ModelRegistry("snowflake://models")
registry.connect()

# Register new model
version = registry.register_model(
    model_name="signal_imputation_v1",
    model_path="models/artifacts",
    metrics={"rmse": 0.15, "mae": 0.10}
)

# Promote to production
registry.promote_model(
    model_name="signal_imputation_v1",
    version=version,
    stage=ModelStage.PRODUCTION
)
```

## Model Types

- **XGBoost**: Gradient boosting for structured data
- **Random Forest**: Ensemble learning for robustness
- **Agent Model**: Adaptive strategy selection
- **Deep Learning**: Neural networks for complex patterns
