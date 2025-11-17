-- Database Grants Setup for Network Signal Imputation Pipeline
-- This script sets up roles and grants for the ML pipeline

-- ============================================================================
-- Role Creation
-- ============================================================================

-- Create roles if they don't exist
CREATE ROLE IF NOT EXISTS ML_ADMIN_ROLE 
    COMMENT = 'Administrator role for ML pipeline';
    
CREATE ROLE IF NOT EXISTS ML_DEVELOPER_ROLE 
    COMMENT = 'Developer role for ML pipeline development';
    
CREATE ROLE IF NOT EXISTS ML_INFERENCE_ROLE 
    COMMENT = 'Role for ML inference execution';
    
CREATE ROLE IF NOT EXISTS ML_MONITORING_ROLE 
    COMMENT = 'Role for monitoring and observability';

CREATE ROLE IF NOT EXISTS ML_DATA_SCIENTIST_ROLE
    COMMENT = 'Role for data scientists and analysts';

-- ============================================================================
-- Database and Schema Grants
-- ============================================================================

-- Grant database usage
GRANT USAGE ON DATABASE ML_DATABASE TO ROLE ML_ADMIN_ROLE;
GRANT USAGE ON DATABASE ML_DATABASE TO ROLE ML_DEVELOPER_ROLE;
GRANT USAGE ON DATABASE ML_DATABASE TO ROLE ML_INFERENCE_ROLE;
GRANT USAGE ON DATABASE ML_DATABASE TO ROLE ML_MONITORING_ROLE;
GRANT USAGE ON DATABASE ML_DATABASE TO ROLE ML_DATA_SCIENTIST_ROLE;

-- Grant schema usage
GRANT USAGE ON SCHEMA ML_DATABASE.ML_SCHEMA TO ROLE ML_ADMIN_ROLE;
GRANT USAGE ON SCHEMA ML_DATABASE.ML_SCHEMA TO ROLE ML_DEVELOPER_ROLE;
GRANT USAGE ON SCHEMA ML_DATABASE.ML_SCHEMA TO ROLE ML_INFERENCE_ROLE;
GRANT USAGE ON SCHEMA ML_DATABASE.ML_SCHEMA TO ROLE ML_MONITORING_ROLE;
GRANT USAGE ON SCHEMA ML_DATABASE.ML_SCHEMA TO ROLE ML_DATA_SCIENTIST_ROLE;

GRANT USAGE ON SCHEMA ML_DATABASE.FEATURE_STORE TO ROLE ML_ADMIN_ROLE;
GRANT USAGE ON SCHEMA ML_DATABASE.FEATURE_STORE TO ROLE ML_DEVELOPER_ROLE;
GRANT USAGE ON SCHEMA ML_DATABASE.FEATURE_STORE TO ROLE ML_INFERENCE_ROLE;
GRANT USAGE ON SCHEMA ML_DATABASE.FEATURE_STORE TO ROLE ML_DATA_SCIENTIST_ROLE;

-- ============================================================================
-- Warehouse Grants
-- ============================================================================

-- Training warehouse (larger, for model training)
GRANT USAGE ON WAREHOUSE TRAINING_WH TO ROLE ML_ADMIN_ROLE;
GRANT USAGE ON WAREHOUSE TRAINING_WH TO ROLE ML_DEVELOPER_ROLE;
GRANT OPERATE ON WAREHOUSE TRAINING_WH TO ROLE ML_DEVELOPER_ROLE;

-- Inference warehouse (optimized for low latency)
GRANT USAGE ON WAREHOUSE INFERENCE_WH TO ROLE ML_ADMIN_ROLE;
GRANT USAGE ON WAREHOUSE INFERENCE_WH TO ROLE ML_INFERENCE_ROLE;
GRANT MONITOR ON WAREHOUSE INFERENCE_WH TO ROLE ML_MONITORING_ROLE;

-- Analytics warehouse (for monitoring and analysis)
GRANT USAGE ON WAREHOUSE ANALYTICS_WH TO ROLE ML_MONITORING_ROLE;
GRANT USAGE ON WAREHOUSE ANALYTICS_WH TO ROLE ML_DATA_SCIENTIST_ROLE;

-- ============================================================================
-- Table Grants
-- ============================================================================

-- Raw data tables
GRANT SELECT ON ALL TABLES IN SCHEMA ML_DATABASE.RAW_DATA TO ROLE ML_DEVELOPER_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA ML_DATABASE.RAW_DATA TO ROLE ML_DATA_SCIENTIST_ROLE;

-- Feature store tables
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA ML_DATABASE.FEATURE_STORE 
    TO ROLE ML_DEVELOPER_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA ML_DATABASE.FEATURE_STORE 
    TO ROLE ML_INFERENCE_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA ML_DATABASE.FEATURE_STORE 
    TO ROLE ML_DATA_SCIENTIST_ROLE;

-- Model predictions table
GRANT SELECT, INSERT ON TABLE ML_DATABASE.ML_SCHEMA.MODEL_PREDICTIONS 
    TO ROLE ML_INFERENCE_ROLE;
GRANT SELECT ON TABLE ML_DATABASE.ML_SCHEMA.MODEL_PREDICTIONS 
    TO ROLE ML_MONITORING_ROLE;

-- Model registry table
GRANT SELECT, INSERT, UPDATE ON TABLE ML_DATABASE.ML_SCHEMA.MODEL_REGISTRY 
    TO ROLE ML_DEVELOPER_ROLE;
GRANT SELECT ON TABLE ML_DATABASE.ML_SCHEMA.MODEL_REGISTRY 
    TO ROLE ML_INFERENCE_ROLE;

-- ============================================================================
-- View Grants
-- ============================================================================

-- Feature engineering views
GRANT SELECT ON ALL VIEWS IN SCHEMA ML_DATABASE.FEATURE_STORE 
    TO ROLE ML_DEVELOPER_ROLE;
GRANT SELECT ON ALL VIEWS IN SCHEMA ML_DATABASE.FEATURE_STORE 
    TO ROLE ML_INFERENCE_ROLE;
GRANT SELECT ON ALL VIEWS IN SCHEMA ML_DATABASE.FEATURE_STORE 
    TO ROLE ML_DATA_SCIENTIST_ROLE;

-- Monitoring views
GRANT SELECT ON ALL VIEWS IN SCHEMA ML_DATABASE.MONITORING 
    TO ROLE ML_MONITORING_ROLE;
GRANT SELECT ON ALL VIEWS IN SCHEMA ML_DATABASE.MONITORING 
    TO ROLE ML_ADMIN_ROLE;

-- ============================================================================
-- Function Grants
-- ============================================================================

-- Inference function
GRANT USAGE ON FUNCTION ML_DATABASE.ML_SCHEMA.SIGNAL_IMPUTATION_INFERENCE(VARCHAR, TIMESTAMP_NTZ, OBJECT)
    TO ROLE ML_INFERENCE_ROLE;
    
-- Allow developers to test inference function
GRANT USAGE ON FUNCTION ML_DATABASE.ML_SCHEMA.SIGNAL_IMPUTATION_INFERENCE(VARCHAR, TIMESTAMP_NTZ, OBJECT)
    TO ROLE ML_DEVELOPER_ROLE;

-- ============================================================================
-- Stage Grants (for model artifacts)
-- ============================================================================

-- Model artifacts stage
GRANT READ ON STAGE ML_DATABASE.ML_SCHEMA.MODEL_ARTIFACTS 
    TO ROLE ML_INFERENCE_ROLE;
GRANT READ, WRITE ON STAGE ML_DATABASE.ML_SCHEMA.MODEL_ARTIFACTS 
    TO ROLE ML_DEVELOPER_ROLE;

-- Feature store stage
GRANT READ ON STAGE ML_DATABASE.FEATURE_STORE.FEATURE_DATA 
    TO ROLE ML_INFERENCE_ROLE;
GRANT READ, WRITE ON STAGE ML_DATABASE.FEATURE_STORE.FEATURE_DATA 
    TO ROLE ML_DEVELOPER_ROLE;

-- ============================================================================
-- Future Grants (for new objects)
-- ============================================================================

-- Automatically grant on new tables
GRANT SELECT ON FUTURE TABLES IN SCHEMA ML_DATABASE.FEATURE_STORE 
    TO ROLE ML_INFERENCE_ROLE;
GRANT SELECT, INSERT, UPDATE ON FUTURE TABLES IN SCHEMA ML_DATABASE.FEATURE_STORE 
    TO ROLE ML_DEVELOPER_ROLE;

-- Automatically grant on new views
GRANT SELECT ON FUTURE VIEWS IN SCHEMA ML_DATABASE.FEATURE_STORE 
    TO ROLE ML_INFERENCE_ROLE;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA ML_DATABASE.MONITORING 
    TO ROLE ML_MONITORING_ROLE;

-- ============================================================================
-- Integration Grants
-- ============================================================================

-- Allow model registry integration
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE ML_DEVELOPER_ROLE;
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE ML_INFERENCE_ROLE;

-- ============================================================================
-- Admin Grants
-- ============================================================================

-- Admin role gets all privileges
GRANT ALL PRIVILEGES ON DATABASE ML_DATABASE TO ROLE ML_ADMIN_ROLE;
GRANT ALL PRIVILEGES ON ALL SCHEMAS IN DATABASE ML_DATABASE TO ROLE ML_ADMIN_ROLE;
GRANT ALL PRIVILEGES ON ALL TABLES IN DATABASE ML_DATABASE TO ROLE ML_ADMIN_ROLE;
GRANT ALL PRIVILEGES ON ALL VIEWS IN DATABASE ML_DATABASE TO ROLE ML_ADMIN_ROLE;

-- Admin can manage roles
GRANT ROLE ML_DEVELOPER_ROLE TO ROLE ML_ADMIN_ROLE;
GRANT ROLE ML_INFERENCE_ROLE TO ROLE ML_ADMIN_ROLE;
GRANT ROLE ML_MONITORING_ROLE TO ROLE ML_ADMIN_ROLE;
GRANT ROLE ML_DATA_SCIENTIST_ROLE TO ROLE ML_ADMIN_ROLE;

-- ============================================================================
-- User-to-Role Assignments
-- ============================================================================

-- Assign roles to users (update with actual usernames)
-- GRANT ROLE ML_ADMIN_ROLE TO USER admin_user;
-- GRANT ROLE ML_DEVELOPER_ROLE TO USER dev_user;
-- GRANT ROLE ML_INFERENCE_ROLE TO USER inference_service_account;
-- GRANT ROLE ML_MONITORING_ROLE TO USER monitoring_service_account;
-- GRANT ROLE ML_DATA_SCIENTIST_ROLE TO USER data_scientist_user;

-- ============================================================================
-- Service Account Setup
-- ============================================================================

-- Create service account for inference
-- CREATE USER IF NOT EXISTS ML_INFERENCE_SERVICE
--     PASSWORD = 'secure_password'
--     DEFAULT_ROLE = ML_INFERENCE_ROLE
--     DEFAULT_WAREHOUSE = INFERENCE_WH
--     COMMENT = 'Service account for ML inference';

-- GRANT ROLE ML_INFERENCE_ROLE TO USER ML_INFERENCE_SERVICE;

-- Create service account for monitoring
-- CREATE USER IF NOT EXISTS ML_MONITORING_SERVICE
--     PASSWORD = 'secure_password'
--     DEFAULT_ROLE = ML_MONITORING_ROLE
--     DEFAULT_WAREHOUSE = ANALYTICS_WH
--     COMMENT = 'Service account for ML monitoring';

-- GRANT ROLE ML_MONITORING_ROLE TO USER ML_MONITORING_SERVICE;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify roles were created
SHOW ROLES LIKE 'ML_%';

-- Verify grants for a specific role
SHOW GRANTS TO ROLE ML_INFERENCE_ROLE;
SHOW GRANTS TO ROLE ML_DEVELOPER_ROLE;
SHOW GRANTS TO ROLE ML_MONITORING_ROLE;

-- Verify warehouse grants
SHOW GRANTS ON WAREHOUSE INFERENCE_WH;
SHOW GRANTS ON WAREHOUSE TRAINING_WH;

-- Verify database grants
SHOW GRANTS ON DATABASE ML_DATABASE;

-- ============================================================================
-- Revocation (if needed)
-- ============================================================================

-- To revoke all grants from a role (use with caution):
-- REVOKE ALL PRIVILEGES ON DATABASE ML_DATABASE FROM ROLE ML_INFERENCE_ROLE;
-- REVOKE USAGE ON WAREHOUSE INFERENCE_WH FROM ROLE ML_INFERENCE_ROLE;

-- To drop a role (use with extreme caution):
-- DROP ROLE IF EXISTS ML_INFERENCE_ROLE;
