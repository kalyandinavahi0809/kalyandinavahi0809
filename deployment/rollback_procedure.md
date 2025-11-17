# Rollback Procedure

## When to Rollback

Execute rollback if you observe:
- Model RMSE exceeds 0.30 (50% degradation from baseline)
- Inference latency P95 exceeds 1000ms
- Error rate exceeds 5%
- Critical data quality issues
- System instability or crashes
- Security vulnerabilities discovered

## Rollback Decision Matrix

| Issue Severity | Response Time | Action |
|---------------|---------------|--------|
| Critical | Immediate | Execute full rollback |
| High | < 1 hour | Evaluate and decide |
| Medium | < 4 hours | Monitor and prepare |
| Low | Next maintenance window | Schedule fix |

## Pre-Rollback Checklist

- [ ] Confirm rollback is necessary
- [ ] Identify root cause (if known)
- [ ] Notify stakeholders
- [ ] Document current state
- [ ] Identify target rollback version
- [ ] Verify backup availability

## Rollback Steps

### 1. Immediate Actions (< 5 minutes)

#### Stop New Predictions
```sql
-- Disable inference function
ALTER FUNCTION SIGNAL_IMPUTATION_INFERENCE SET COMMENT = 'DISABLED - ROLLING BACK';

-- Route traffic to previous version
USE SCHEMA ML_SCHEMA_PREVIOUS;
```

#### Notify Team
- Post in incident channel: `#ml-incidents`
- Update status page
- Send email to stakeholders

### 2. Restore Model (5-15 minutes)

#### Option A: Revert Model Registry
```python
from modeling.registry import ModelRegistry, ModelStage

registry = ModelRegistry("snowflake://models")
registry.connect()

# Promote previous production model
registry.promote_model(
    model_name="signal_imputation_v1",
    version="PREVIOUS_VERSION",  # e.g., "20240101_120000"
    stage=ModelStage.PRODUCTION
)
```

#### Option B: Use Snowflake Model Registry
```sql
-- List model versions
SHOW MODELS LIKE 'signal_imputation%';

-- Promote previous version
ALTER MODEL signal_imputation_v1 
  SET DEFAULT_VERSION = 'PREVIOUS_VERSION';
```

### 3. Restore Feature Store (5-10 minutes)

```sql
-- Switch to previous feature definitions
USE DATABASE ML_DATABASE;
USE SCHEMA FEATURE_STORE_BACKUP;

-- Verify features
SELECT COUNT(*) FROM VW_TRAINING_FEATURES;

-- Restore views if needed
CREATE OR REPLACE VIEW VW_TRAINING_FEATURES AS 
  SELECT * FROM FEATURE_STORE_BACKUP.VW_TRAINING_FEATURES;
```

### 4. Restore SQL Objects (5-10 minutes)

```sql
-- Restore inference function from backup
CREATE OR REPLACE FUNCTION SIGNAL_IMPUTATION_INFERENCE(...)
AS
$$
-- [Previous function code from backup]
$$;

-- Restore views
@view_definitions_backup.sql

-- Verify restoration
SELECT * FROM TABLE(SIGNAL_IMPUTATION_INFERENCE(
    'TEST_001',
    CURRENT_TIMESTAMP(),
    OBJECT_CONSTRUCT('signal_strength', -75)
)) LIMIT 1;
```

### 5. Restore Configuration (2-5 minutes)

```bash
# Revert config.yaml
git checkout PREVIOUS_COMMIT -- config.yaml

# Update environment variables
export MODEL_VERSION="PREVIOUS_VERSION"
export FEATURE_STORE_SCHEMA="feature_store_backup"

# Restart services if needed
kubectl rollout undo deployment/signal-imputation-service
```

### 6. Verify Rollback (10-15 minutes)

#### Test Inference
```python
from modeling.pipeline import SignalImputationPipeline

# Test with sample data
pipeline = SignalImputationPipeline(config)
predictions = pipeline.predict(test_data)

# Verify predictions
assert predictions.shape[0] > 0
assert not predictions.isna().any()
```

#### Check Metrics
```sql
-- Verify model performance
SELECT 
    model_version,
    AVG(ABS(predicted_value - actual_value)) as mae,
    SQRT(AVG(POWER(predicted_value - actual_value, 2))) as rmse
FROM model_predictions
WHERE prediction_timestamp >= DATEADD(minute, -15, CURRENT_TIMESTAMP())
GROUP BY model_version;

-- Check prediction volume
SELECT 
    COUNT(*) as prediction_count,
    AVG(inference_time_ms) as avg_latency_ms
FROM inference_logs
WHERE timestamp >= DATEADD(minute, -15, CURRENT_TIMESTAMP());
```

#### Monitor Dashboard
- [ ] Check RMSE is back to acceptable levels (< 0.20)
- [ ] Verify MAE is within bounds (< 0.15)
- [ ] Confirm latency is acceptable (P95 < 500ms)
- [ ] Review error logs for issues

### 7. Re-enable Services (5 minutes)

```sql
-- Re-enable inference function
ALTER FUNCTION SIGNAL_IMPUTATION_INFERENCE 
  SET COMMENT = 'Production inference function';

-- Switch back to production schema
USE SCHEMA ML_SCHEMA;
```

## Post-Rollback Actions

### Immediate (< 1 hour)

- [ ] Confirm system stability
- [ ] Monitor metrics continuously
- [ ] Document rollback details
- [ ] Update incident log
- [ ] Communicate status to stakeholders

### Short-term (< 24 hours)

- [ ] Conduct post-mortem meeting
- [ ] Identify root cause
- [ ] Create fix plan
- [ ] Update rollback procedure if needed
- [ ] Review monitoring gaps

### Long-term (< 1 week)

- [ ] Implement fixes
- [ ] Add additional tests
- [ ] Improve monitoring
- [ ] Update documentation
- [ ] Plan re-deployment

## Rollback Verification Checklist

- [ ] Model version reverted successfully
- [ ] Feature store restored
- [ ] SQL objects working
- [ ] Predictions generating correctly
- [ ] Performance metrics acceptable
- [ ] No errors in logs
- [ ] Monitoring dashboards updated
- [ ] Stakeholders notified

## Common Issues During Rollback

### Issue: Previous model not found
**Solution:**
```sql
-- Check model backups
SELECT * FROM model_registry_backup 
WHERE model_name = 'signal_imputation_v1'
ORDER BY created_at DESC;

-- Restore from backup location
COPY INTO @models/signal_imputation_v1/
FROM @models_backup/PREVIOUS_VERSION/;
```

### Issue: Feature definitions changed
**Solution:**
```python
# Use feature store version pinning
from feature_store.feature_definitions import SIGNAL_FEATURES

# Load specific version
features = load_features(version="PREVIOUS_VERSION")
```

### Issue: Database permissions issues
**Solution:**
```sql
-- Re-grant necessary permissions
GRANT USAGE ON FUNCTION SIGNAL_IMPUTATION_INFERENCE TO ROLE ML_INFERENCE_ROLE;
GRANT SELECT ON ALL VIEWS IN SCHEMA FEATURE_STORE_BACKUP TO ROLE ML_DEVELOPER_ROLE;
```

## Emergency Contacts

| Role | Name | Contact | Backup |
|------|------|---------|--------|
| ML Lead | [Name] | [Phone/Email] | [Name] |
| DevOps | [Name] | [Phone/Email] | [Name] |
| Data Engineer | [Name] | [Phone/Email] | [Name] |
| On-call Engineer | [Check PagerDuty] | | |

## Rollback Log Template

```
Date/Time: [YYYY-MM-DD HH:MM:SS]
Initiated By: [Name]
Reason: [Brief description]
Previous Version: [Version ID]
New Version (rolled back): [Version ID]
Duration: [Minutes]
Impact: [Description]
Status: [Success/Partial/Failed]
Notes: [Additional details]
```

## Communication Template

**Subject:** [RESOLVED/IN PROGRESS] ML Model Rollback - Network Signal Imputation

**Body:**
```
Status: [IN PROGRESS / COMPLETED]
Start Time: [Time]
End Time: [Time] (if completed)

Issue:
[Description of issue that triggered rollback]

Actions Taken:
- [List of rollback steps completed]

Current Status:
[Current state of system]

Impact:
[Description of impact on users/system]

Next Steps:
[What happens next]

Contact: [Name] for questions
```

## Testing Rollback Procedure

Regularly test this procedure in staging:
- [ ] Monthly rollback drill
- [ ] Verify backup restoration
- [ ] Test communication channels
- [ ] Update procedure based on learnings
