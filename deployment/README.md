# Deployment

This directory contains deployment procedures and checklists for the Network Signal Imputation pipeline.

## Files

- **production_checklist.md**: Comprehensive pre-deployment and post-deployment checklist
- **rollback_procedure.md**: Step-by-step rollback instructions
- **grants_setup.sql**: Database roles and permissions setup
- **README.md**: This file

## Deployment Strategy

### Blue-Green Deployment
We use a blue-green deployment strategy to minimize downtime:
1. Deploy new version to staging environment
2. Run validation tests
3. Switch traffic to new version
4. Monitor for issues
5. Keep old version ready for rollback

### Deployment Environments

| Environment | Purpose | Model Version | Data |
|-------------|---------|---------------|------|
| Development | Feature development | Latest | Synthetic |
| Staging | Pre-production testing | Release candidates | Subset of prod |
| Production | Live inference | Stable releases | Full production |

## Pre-Deployment Steps

1. **Code Review**
   ```bash
   # Ensure all PRs are reviewed and approved
   git log --oneline origin/main..HEAD
   ```

2. **Run Tests**
   ```bash
   # Run full test suite
   pytest tests/ -v --cov
   
   # Run integration tests
   pytest tests/test_integration.py -v
   ```

3. **Security Scan**
   ```bash
   # Run security checks
   bandit -r modeling/ feature_store/ monitoring/
   ```

4. **Build and Package**
   ```bash
   # Build package
   python setup.py sdist bdist_wheel
   
   # Verify package
   twine check dist/*
   ```

## Deployment Process

### 1. Deploy to Staging

```bash
# Set environment
export ENV=staging

# Deploy feature store
python feature_store/setup_feature_store.py --env staging

# Deploy SQL objects
snowsql -c staging -f sql/view_definitions.sql
snowsql -c staging -f sql/inference_table_function.sql

# Deploy model
python modeling/pipeline.py --env staging --mode deploy
```

### 2. Run Validation Tests

```python
from tests.test_integration import run_staging_validation

# Run validation suite
results = run_staging_validation()
assert results["all_passed"], "Validation failed"
```

### 3. Deploy to Production

```bash
# Set environment
export ENV=production

# Execute deployment checklist
# See production_checklist.md

# Deploy with rollback protection
python deploy.py --env production --enable-rollback
```

## Database Setup

### Initial Setup

```sql
-- 1. Create database and schemas
CREATE DATABASE IF NOT EXISTS ML_DATABASE;
CREATE SCHEMA IF NOT EXISTS ML_DATABASE.ML_SCHEMA;
CREATE SCHEMA IF NOT EXISTS ML_DATABASE.FEATURE_STORE;
CREATE SCHEMA IF NOT EXISTS ML_DATABASE.MONITORING;

-- 2. Setup roles and grants
@deployment/grants_setup.sql

-- 3. Create warehouses
CREATE WAREHOUSE IF NOT EXISTS TRAINING_WH
    WAREHOUSE_SIZE = 'LARGE'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;

CREATE WAREHOUSE IF NOT EXISTS INFERENCE_WH
    WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;
```

### Verify Setup

```sql
-- Check database objects
SHOW DATABASES LIKE 'ML_%';
SHOW SCHEMAS IN DATABASE ML_DATABASE;
SHOW TABLES IN SCHEMA ML_DATABASE.ML_SCHEMA;
SHOW VIEWS IN SCHEMA ML_DATABASE.FEATURE_STORE;
SHOW FUNCTIONS IN SCHEMA ML_DATABASE.ML_SCHEMA;

-- Check permissions
SHOW GRANTS TO ROLE ML_INFERENCE_ROLE;

-- Test inference
SELECT * FROM TABLE(SIGNAL_IMPUTATION_INFERENCE(
    'TEST_001',
    CURRENT_TIMESTAMP(),
    OBJECT_CONSTRUCT('signal_strength', -75)
));
```

## Monitoring Setup

### Deploy Monitoring Components

```bash
# Deploy quality checks
python monitoring/quality_checks.py --setup

# Setup drift detection
python monitoring/drift_detection.py --init-reference-data

# Configure alerts
python monitoring/alert_rules.py --deploy
```

### Configure Dashboard

```bash
# Deploy dashboard config
grafana-cli dashboard import monitoring/dashboard_config.json
```

## Rollback Process

If issues occur, follow the rollback procedure:

```bash
# Execute rollback
python scripts/rollback.py --to-version v1.2.3

# Or follow manual procedure
# See deployment/rollback_procedure.md
```

## Post-Deployment

### Immediate Checks (First Hour)

```bash
# Monitor predictions
python scripts/monitor_predictions.py --duration 60

# Check error rates
python scripts/check_errors.py --threshold 0.05

# Review metrics
python scripts/report_metrics.py
```

### Smoke Tests

```python
from tests.test_smoke import run_smoke_tests

# Run smoke tests
results = run_smoke_tests()
print(f"Smoke tests: {results['passed']}/{results['total']}")
```

## Deployment Schedule

- **Staging**: Continuous deployment on merge to `develop`
- **Production**: Weekly releases on Wednesdays at 10:00 AM
- **Hotfixes**: As needed, following expedited procedure

## Change Management

All production deployments require:
1. Change request ticket
2. Approved pull request
3. Successful staging deployment
4. Sign-off from tech lead
5. Communication to stakeholders

## Emergency Procedures

### Critical Issue
1. Execute immediate rollback
2. Post in `#ml-incidents` channel
3. Page on-call engineer
4. Follow incident response procedure

### Degraded Performance
1. Increase monitoring frequency
2. Prepare rollback
3. Investigate root cause
4. Deploy fix or rollback within 1 hour

## Contacts

- **ML Team Lead**: [Name] - [Email]
- **DevOps Lead**: [Name] - [Email]
- **On-Call**: Check PagerDuty rotation
- **Escalation**: [Name] - [Email]

## Best Practices

1. **Always test in staging first**
2. **Deploy during low-traffic windows**
3. **Monitor closely for first 24 hours**
4. **Keep rollback plan ready**
5. **Document all changes**
6. **Communicate with stakeholders**
7. **Run security scans before deployment**
8. **Backup before deployment**

## Troubleshooting

### Common Issues

**Issue**: Inference function not found
```sql
-- Check function exists
SHOW FUNCTIONS LIKE 'SIGNAL_IMPUTATION%';

-- Recreate function
@sql/inference_table_function.sql
```

**Issue**: Permission denied
```sql
-- Check grants
SHOW GRANTS TO ROLE ML_INFERENCE_ROLE;

-- Re-run grants script
@deployment/grants_setup.sql
```

**Issue**: Model not loading
```python
from modeling.registry import ModelRegistry

# Check model registry
registry = ModelRegistry("snowflake://models")
models = registry.list_models()
print(models)
```

## Maintenance Windows

Regular maintenance schedule:
- **Weekly**: Sunday 2:00 AM - 4:00 AM EST
- **Monthly**: First Sunday, 2:00 AM - 6:00 AM EST
- **Emergency**: As needed with 2-hour notice

## Documentation

Keep updated:
- Architecture diagrams
- Deployment runbooks
- Incident reports
- Performance baselines
- Configuration changes
