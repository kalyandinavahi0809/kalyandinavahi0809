# Monitoring

This directory contains monitoring and observability components for the Network Signal Imputation pipeline.

## Files

- **quality_checks.py**: Comprehensive data quality monitoring
- **drift_detection.py**: Data and model drift detection
- **dashboard_config.json**: Monitoring dashboard configuration
- **alert_rules.py**: Alert rule definitions and management

## Monitoring Architecture

### Data Quality Monitoring
- Missing data detection
- Value range validation
- Data type checking
- Duplicate detection
- Freshness monitoring

### Drift Detection
- Feature drift (PSI-based)
- Prediction drift
- Concept drift
- Distribution shift detection

### Alerting
- Configurable alert rules
- Multiple severity levels
- Alert channels (email, Slack, PagerDuty)
- Cooldown periods to prevent alert fatigue

## Usage

### Run Quality Checks

```python
from monitoring.quality_checks import QualityChecker

config = {
    "thresholds": {
        "max_missing_percentage": 30,
        "max_duplicates": 0,
        "max_data_age_hours": 24
    },
    "value_ranges": {
        "signal_strength": (-120, 0),
        "bandwidth_usage": (0, 100)
    }
}

checker = QualityChecker(config)
results = checker.run_all_checks(df)

print(f"Checks passed: {results['summary']['passed']}")
print(f"Checks failed: {results['summary']['failed']}")
```

### Detect Drift

```python
from monitoring.drift_detection import DriftDetector

config = {
    "performance_drift_threshold": 0.15,
    "feature_drift_threshold": 0.1
}

detector = DriftDetector(config)
detector.set_reference_data(reference_df)

# Check for feature drift
drift_results = detector.detect_feature_drift(current_df)

for feature, result in drift_results.items():
    if result["drift_detected"]:
        print(f"Drift detected in {feature}: PSI={result['psi']:.4f}")
```

### Setup Alerts

```python
from monitoring.alert_rules import AlertManager, AlertRule, AlertSeverity

config = {
    "channels": [
        {"type": "email", "recipients": ["ml-team@company.com"]},
        {"type": "slack", "webhook_url": "https://hooks.slack.com/..."}
    ]
}

manager = AlertManager(config)

# Add custom rule
custom_rule = AlertRule(
    name="custom_check",
    condition=lambda m: m.get("custom_metric", 0) > 100,
    severity=AlertSeverity.WARNING,
    message="Custom metric exceeded threshold"
)
manager.add_rule(custom_rule)

# Evaluate rules
metrics = {
    "rmse": 0.25,
    "mae": 0.18,
    "missing_percentage": 15.5
}

alerts = manager.evaluate_rules(metrics)
if alerts:
    manager.send_alerts(alerts)
```

### Dashboard Configuration

The `dashboard_config.json` file defines:
- Panel layouts and visualizations
- Metric queries and thresholds
- Alert configurations
- Data source connections

Deploy the dashboard to your monitoring platform (Grafana, Tableau, etc.) using this configuration.

## Metrics to Monitor

### Model Performance
- RMSE (Root Mean Square Error)
- MAE (Mean Absolute Error)
- R² Score
- Prediction confidence

### Data Quality
- Missing data percentage
- Data freshness (hours since last update)
- Duplicate records
- Value range violations

### Drift Indicators
- PSI (Population Stability Index) per feature
- Performance degradation percentage
- Distribution shifts

### Infrastructure
- Inference latency (P50, P95, P99)
- Prediction volume
- Error rates
- System resource utilization

## Alert Severity Levels

- **INFO**: Informational notifications
- **WARNING**: Issues requiring attention
- **CRITICAL**: Severe issues requiring immediate action

## Best Practices

1. **Baseline Establishment**: Set reference data from a stable period
2. **Regular Reviews**: Review drift reports weekly
3. **Alert Tuning**: Adjust thresholds based on false positive rates
4. **Automated Responses**: Implement automatic model retraining triggers
5. **Dashboard Review**: Check dashboards daily
6. **Incident Response**: Document and analyze alert patterns
