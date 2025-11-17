# Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Network Signal Imputation ML pipeline to production environments.

## Deployment Strategy

We use a **Blue-Green Deployment** strategy with the following characteristics:
- Zero-downtime deployments
- Quick rollback capability
- Gradual traffic migration
- Automated health checks

## Prerequisites

### Required Access
- [ ] Snowflake account with appropriate permissions
- [ ] GitHub repository access
- [ ] AWS S3 access (for model artifacts)
- [ ] PagerDuty/Slack access (for alerts)

### Required Tools
```bash
# Install CLI tools
pip install snowflake-connector-python
pip install awscli
brew install snowsql  # or apt-get install snowsql

# Verify installations
snowsql --version
aws --version
python --version
```

### Environment Setup
```bash
# Set environment variables
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
export SNOWFLAKE_DATABASE="ML_DATABASE"
export SNOWFLAKE_SCHEMA="ML_SCHEMA"
export AWS_REGION="us-east-1"
export MODEL_REGISTRY_URI="snowflake://models"
```

## Deployment Environments

### Development
- **Purpose**: Feature development and testing
- **Data**: Synthetic/sampled data
- **Model**: Latest experimental versions
- **Updates**: Continuous (on every commit)

### Staging
- **Purpose**: Pre-production validation
- **Data**: Subset of production data
- **Model**: Release candidates
- **Updates**: Daily (automated)

### Production
- **Purpose**: Live inference serving
- **Data**: Full production dataset
- **Model**: Stable, validated versions
- **Updates**: Weekly (scheduled) or on-demand

## Pre-Deployment Checklist

See [Production Checklist](../deployment/production_checklist.md) for detailed checklist.

### Quick Verification

```bash
# Run pre-deployment script
./scripts/pre_deployment_check.sh

# Output should show all checks passing:
# ✓ Tests passing
# ✓ Security scan clean
# ✓ Model performance acceptable
# ✓ Feature store ready
# ✓ Permissions configured
```

## Deployment Steps

### Step 1: Prepare Release

```bash
# Create release branch
git checkout -b release/v2.0.0

# Update version
echo "2.0.0" > VERSION

# Tag release
git tag -a v2.0.0 -m "Release version 2.0.0"
git push origin v2.0.0
```

### Step 2: Deploy to Staging

```bash
# Set environment
export ENV=staging

# Deploy feature store
python feature_store/setup_feature_store.py \
    --env staging \
    --validate

# Deploy SQL objects
snowsql -c staging \
    -f sql/view_definitions.sql \
    -f sql/inference_table_function.sql

# Deploy model
python modeling/pipeline.py \
    --env staging \
    --mode deploy \
    --model-version v2.0.0

# Verify deployment
python scripts/verify_deployment.py --env staging
```

### Step 3: Run Staging Tests

```bash
# Run integration tests
pytest tests/ -m integration --env staging -v

# Run smoke tests
python scripts/smoke_tests.py --env staging

# Performance tests
python scripts/performance_tests.py --env staging

# All tests must pass before proceeding
```

### Step 4: Deploy to Production

```bash
# Set environment
export ENV=production

# Create backup
python scripts/backup_production.py

# Deploy with blue-green strategy
python scripts/deploy_production.py \
    --version v2.0.0 \
    --strategy blue-green \
    --health-check-timeout 300

# Monitor deployment
python scripts/monitor_deployment.py \
    --duration 3600 \
    --alert-on-error
```

### Step 5: Validate Production

```bash
# Run production smoke tests
python scripts/smoke_tests.py --env production

# Check metrics
python scripts/check_metrics.py \
    --duration 60 \
    --thresholds config/production_thresholds.yml

# Verify inference
python scripts/test_inference.py \
    --sample-size 100 \
    --env production
```

## Database Deployment

### Initial Setup

```sql
-- Run these scripts in order:

-- 1. Create database objects
@sql/create_database.sql

-- 2. Setup roles and permissions
@deployment/grants_setup.sql

-- 3. Create views
@sql/view_definitions.sql

-- 4. Deploy inference function
@sql/inference_table_function.sql
```

### Migrations

```sql
-- Example migration script
-- File: migrations/20240115_add_latency_column.sql

-- Add new column
ALTER TABLE raw_signals 
ADD COLUMN latency_ms FLOAT;

-- Update view
CREATE OR REPLACE VIEW VW_TRAINING_FEATURES AS
SELECT 
    *,
    latency_ms  -- New feature
FROM raw_signals;

-- Verify migration
SELECT COUNT(*) FROM VW_TRAINING_FEATURES;
```

### Rollback Database Changes

```sql
-- Rollback migration
-- File: migrations/20240115_add_latency_column_rollback.sql

-- Remove column
ALTER TABLE raw_signals 
DROP COLUMN latency_ms;

-- Restore view
CREATE OR REPLACE VIEW VW_TRAINING_FEATURES AS
SELECT 
    *  -- Without latency_ms
FROM raw_signals;
```

## Model Deployment

### Deploy New Model Version

```python
from modeling.registry import ModelRegistry, ModelStage

# Initialize registry
registry = ModelRegistry("snowflake://models")

# Register new model
version = registry.register_model(
    model_name="signal_imputation_v2",
    model_path="models/v2.0.0/model.pkl",
    metrics={"rmse": 0.12, "mae": 0.08},
    metadata={
        "git_commit": "abc123",
        "training_date": "2024-01-15"
    }
)

# Promote to production
registry.promote_model(
    model_name="signal_imputation_v2",
    version=version,
    stage=ModelStage.PRODUCTION
)
```

### Gradual Rollout

```python
def gradual_rollout(model_version, stages=[0.1, 0.25, 0.5, 1.0]):
    """Gradually roll out new model version."""
    
    for traffic_percentage in stages:
        # Update traffic routing
        update_traffic_split(
            new_version=model_version,
            traffic_percentage=traffic_percentage
        )
        
        # Monitor for 30 minutes
        metrics = monitor_metrics(duration_minutes=30)
        
        # Check if metrics are acceptable
        if not metrics_acceptable(metrics):
            # Rollback
            rollback_traffic()
            raise Exception("Metrics degraded, rolling back")
        
        print(f"Traffic at {traffic_percentage*100}%, metrics OK")
    
    print("Rollout complete, 100% traffic on new version")
```

## Monitoring Deployment

### Real-time Monitoring

```bash
# Monitor key metrics during deployment
watch -n 5 '
    echo "=== Model Performance ==="
    python scripts/get_metrics.py --metric rmse --window 5m
    
    echo "=== Inference Latency ==="
    python scripts/get_metrics.py --metric latency --window 5m
    
    echo "=== Error Rate ==="
    python scripts/get_metrics.py --metric error_rate --window 5m
'
```

### Automated Health Checks

```python
def health_check():
    """Automated health check post-deployment."""
    
    checks = {
        "inference_working": test_inference(),
        "latency_acceptable": check_latency() < 100,  # ms
        "error_rate_low": check_error_rate() < 0.01,
        "model_loaded": verify_model_loaded(),
        "feature_store_accessible": test_feature_store()
    }
    
    if all(checks.values()):
        return {"status": "healthy", "checks": checks}
    else:
        failed = [k for k, v in checks.items() if not v]
        return {"status": "unhealthy", "failed_checks": failed}
```

## Rollback Procedures

See [Rollback Procedure](../deployment/rollback_procedure.md) for detailed instructions.

### Quick Rollback

```bash
# Immediate rollback to previous version
python scripts/rollback.py \
    --to-version v1.9.0 \
    --reason "High error rate detected"

# Verify rollback
python scripts/verify_deployment.py \
    --expected-version v1.9.0
```

### Automated Rollback Triggers

```python
def auto_rollback_monitor():
    """Monitor metrics and auto-rollback if needed."""
    
    while True:
        metrics = get_current_metrics()
        
        # Check rollback conditions
        if metrics['error_rate'] > 0.05:
            trigger_rollback("High error rate")
        elif metrics['rmse'] > 0.30:
            trigger_rollback("Performance degradation")
        elif metrics['latency_p95'] > 1000:
            trigger_rollback("High latency")
        
        time.sleep(60)  # Check every minute
```

## CI/CD Integration

### GitHub Actions Workflow

See `.github/workflows/deploy.yml` for full workflow.

```yaml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Tests
        run: pytest tests/ -v
      
      - name: Security Scan
        run: bandit -r modeling/ feature_store/
      
      - name: Deploy to Staging
        run: python scripts/deploy.py --env staging
      
      - name: Staging Tests
        run: python scripts/smoke_tests.py --env staging
      
      - name: Deploy to Production
        run: python scripts/deploy.py --env production
        if: success()
      
      - name: Notify Team
        run: python scripts/notify_deployment.py
```

## Traffic Management

### Blue-Green Deployment

```python
def blue_green_deploy(new_version):
    """Execute blue-green deployment."""
    
    # Deploy to green environment
    deploy_to_environment("green", new_version)
    
    # Run health checks on green
    if not health_check("green"):
        raise Exception("Green environment unhealthy")
    
    # Switch traffic to green
    switch_traffic("green")
    
    # Monitor for issues
    monitor_duration_minutes = 30
    if not monitor_stable("green", monitor_duration_minutes):
        # Rollback to blue
        switch_traffic("blue")
        raise Exception("Issues detected, rolled back to blue")
    
    # Success, green is now primary
    print("Deployment successful")
```

### Canary Deployment

```python
def canary_deploy(new_version, canary_percentage=10):
    """Execute canary deployment."""
    
    # Deploy canary
    deploy_canary(new_version, canary_percentage)
    
    # Monitor canary
    canary_metrics = monitor_canary(duration_minutes=30)
    baseline_metrics = monitor_baseline(duration_minutes=30)
    
    # Compare metrics
    if canary_metrics_acceptable(canary_metrics, baseline_metrics):
        # Gradually increase canary traffic
        for pct in [25, 50, 75, 100]:
            update_canary_traffic(pct)
            monitor_canary(duration_minutes=15)
    else:
        # Remove canary
        remove_canary()
        raise Exception("Canary metrics unacceptable")
```

## Post-Deployment

### Immediate (First Hour)

```bash
# Monitor every 5 minutes
for i in {1..12}; do
    python scripts/check_metrics.py
    sleep 300
done
```

### Day 1-7

```bash
# Daily checks
python scripts/daily_health_check.py

# Generate report
python scripts/generate_deployment_report.py \
    --version v2.0.0 \
    --days 7
```

### Week 1-4

```bash
# Weekly review
python scripts/weekly_performance_review.py

# Drift detection
python monitoring/drift_detection.py \
    --compare-to-baseline
```

## Troubleshooting

### Common Issues

#### Issue: High Latency After Deployment

```bash
# Check query performance
python scripts/analyze_slow_queries.py

# Optimize if needed
snowsql -c production -f sql/optimize_queries.sql

# Clear caches
python scripts/clear_feature_cache.py
```

#### Issue: Model Not Loading

```python
# Verify model artifacts
from modeling.registry import ModelRegistry

registry = ModelRegistry("snowflake://models")
model_info = registry.get_model_info("signal_imputation_v2", version)

# Check artifact path
print(f"Artifact path: {model_info['artifact_path']}")

# Verify artifact exists
verify_artifact_exists(model_info['artifact_path'])
```

#### Issue: Permission Errors

```sql
-- Re-run grants
@deployment/grants_setup.sql

-- Verify permissions
SHOW GRANTS TO ROLE ML_INFERENCE_ROLE;

-- Test access
USE ROLE ML_INFERENCE_ROLE;
SELECT * FROM TABLE(SIGNAL_IMPUTATION_INFERENCE(...)) LIMIT 1;
```

## Best Practices

### 1. Always Deploy to Staging First
Never deploy directly to production without staging validation.

### 2. Automate Everything
Use scripts and CI/CD for consistency and repeatability.

### 3. Monitor Closely Post-Deployment
First 24 hours are critical for detecting issues.

### 4. Maintain Rollback Capability
Always keep previous version ready for quick rollback.

### 5. Document Everything
Log all deployments, issues, and resolutions.

### 6. Communicate with Stakeholders
Notify before, during, and after deployments.

### 7. Schedule During Low Traffic
Deploy during maintenance windows when possible.

### 8. Test Rollback Procedures
Regularly test that rollback works as expected.

## Security Considerations

### Secrets Management

```bash
# Never commit secrets to git
# Use environment variables or secret managers

# AWS Secrets Manager
aws secretsmanager get-secret-value \
    --secret-id snowflake/prod/credentials

# GitHub Secrets
# Set in repository settings
```

### Network Security

```bash
# Use VPC endpoints for Snowflake
# Enable IP whitelisting
# Use SSL/TLS for all connections
```

### Audit Logging

```sql
-- Enable audit logging
ALTER ACCOUNT SET LOG_LEVEL = 'INFO';

-- Query audit logs
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE USER_NAME = 'ML_INFERENCE_SERVICE'
    AND START_TIME >= DATEADD(hour, -1, CURRENT_TIMESTAMP())
ORDER BY START_TIME DESC;
```

## Emergency Procedures

### Production Incident

1. **Immediate**: Execute rollback
2. **Communication**: Alert team via Slack/#ml-incidents
3. **Investigation**: Analyze logs and metrics
4. **Fix**: Develop and test fix
5. **Deploy**: Follow standard deployment process
6. **Post-mortem**: Document incident and lessons learned

### Contact Information

- **On-call**: Check PagerDuty rotation
- **ML Lead**: ml-lead@company.com
- **DevOps**: devops-team@company.com
- **Security**: security-team@company.com

## Resources

- [Production Checklist](../deployment/production_checklist.md)
- [Rollback Procedure](../deployment/rollback_procedure.md)
- [Architecture Documentation](architecture.md)
- [Monitoring Guide](../monitoring/README.md)

## Support

For deployment questions or issues:
- **Slack**: #ml-deployments
- **Email**: ml-team@company.com
- **On-call**: PagerDuty rotation
