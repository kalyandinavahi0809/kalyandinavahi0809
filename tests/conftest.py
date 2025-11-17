"""
Pytest configuration and shared fixtures for tests.

This module provides common fixtures and configuration for all tests.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os


# ============================================================================
# Test Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "requires_snowflake: marks tests that require Snowflake connection"
    )


# ============================================================================
# Common Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "database": "TEST_DATABASE",
        "schema": "TEST_SCHEMA",
        "warehouse": "TEST_WH",
        "feature_store": "TEST_FEATURE_STORE",
        "model_registry": "test_registry"
    }


@pytest.fixture
def sample_signal_data():
    """
    Create sample signal data for testing.
    
    Returns:
        DataFrame with synthetic signal data
    """
    n_samples = 100
    timestamps = [datetime.now() - timedelta(hours=i) for i in range(n_samples)]
    
    data = {
        'timestamp': timestamps,
        'signal_id': [f'SIGNAL_{i:03d}' for i in range(n_samples)],
        'signal_strength': np.random.uniform(-120, -30, n_samples),
        'signal_quality': np.random.uniform(0, 100, n_samples),
        'bandwidth_usage': np.random.uniform(0, 100, n_samples),
        'network_type': np.random.choice(['4G', '5G', 'LTE'], n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Introduce missing values (20%)
    for col in ['signal_strength', 'signal_quality', 'bandwidth_usage']:
        mask = np.random.random(n_samples) < 0.2
        df.loc[mask, col] = np.nan
        
    return df


@pytest.fixture
def sample_training_data():
    """
    Create sample training data.
    
    Returns:
        Tuple of (X, y) for training
    """
    n_samples = 1000
    n_features = 10
    
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    
    # Create target with some relationship to features
    y = pd.Series(
        X['feature_0'] * 2 + X['feature_1'] * 1.5 + np.random.randn(n_samples) * 0.5,
        name='target'
    )
    
    return X, y


@pytest.fixture
def temp_directory():
    """
    Create a temporary directory for test files.
    
    Yields:
        Path to temporary directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_csv_file(sample_signal_data, temp_directory):
    """
    Create a temporary CSV file with sample data.
    
    Args:
        sample_signal_data: Sample signal data fixture
        temp_directory: Temporary directory fixture
        
    Returns:
        Path to CSV file
    """
    filepath = os.path.join(temp_directory, 'test_data.csv')
    sample_signal_data.to_csv(filepath, index=False)
    return filepath


@pytest.fixture
def mock_model():
    """
    Create a mock model for testing.
    
    Returns:
        Mock model object
    """
    class MockModel:
        def __init__(self):
            self.is_fitted = False
            
        def fit(self, X, y):
            self.is_fitted = True
            return self
            
        def predict(self, X):
            if not self.is_fitted:
                raise ValueError("Model not fitted")
            return np.random.randn(len(X))
            
        def score(self, X, y):
            return 0.85
            
    return MockModel()


@pytest.fixture
def mock_feature_store():
    """
    Create a mock feature store for testing.
    
    Returns:
        Mock feature store object
    """
    class MockFeatureStore:
        def __init__(self):
            self.features = {}
            
        def add_feature(self, name, data):
            self.features[name] = data
            
        def get_feature(self, name):
            return self.features.get(name)
            
        def list_features(self):
            return list(self.features.keys())
            
    return MockFeatureStore()


@pytest.fixture
def mock_model_registry():
    """
    Create a mock model registry for testing.
    
    Returns:
        Mock model registry object
    """
    class MockModelRegistry:
        def __init__(self):
            self.models = {}
            
        def register_model(self, name, model, metrics):
            version = f"v{len(self.models) + 1}"
            self.models[name] = {
                'model': model,
                'metrics': metrics,
                'version': version
            }
            return version
            
        def get_model(self, name):
            return self.models.get(name, {}).get('model')
            
        def list_models(self):
            return list(self.models.keys())
            
    return MockModelRegistry()


# ============================================================================
# Parametrized Fixtures
# ============================================================================

@pytest.fixture(params=[10, 50, 100, 500])
def sample_sizes(request):
    """Parametrized fixture for different sample sizes."""
    return request.param


@pytest.fixture(params=[0.0, 0.1, 0.2, 0.3])
def missing_rates(request):
    """Parametrized fixture for different missing data rates."""
    return request.param


@pytest.fixture(params=['xgboost', 'random_forest', 'linear_regression'])
def model_types(request):
    """Parametrized fixture for different model types."""
    return request.param


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test."""
    yield
    # Cleanup code here if needed
    pass


# ============================================================================
# Database Fixtures (for integration tests)
# ============================================================================

@pytest.fixture(scope="session")
def snowflake_connection():
    """
    Create Snowflake connection for integration tests.
    
    Skip if connection cannot be established.
    """
    pytest.skip("Snowflake connection not configured for testing")
    # In actual implementation:
    # try:
    #     conn = snowflake.connector.connect(...)
    #     yield conn
    #     conn.close()
    # except Exception:
    #     pytest.skip("Could not connect to Snowflake")


# ============================================================================
# Helper Functions
# ============================================================================

def assert_dataframe_equal(df1, df2, **kwargs):
    """
    Assert two DataFrames are equal with custom handling.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
        **kwargs: Additional arguments for pandas.testing.assert_frame_equal
    """
    pd.testing.assert_frame_equal(
        df1, df2,
        check_dtype=kwargs.get('check_dtype', True),
        check_names=kwargs.get('check_names', True),
        check_exact=kwargs.get('check_exact', False),
        rtol=kwargs.get('rtol', 1e-5),
        atol=kwargs.get('atol', 1e-8)
    )


def create_test_data_with_patterns(n_samples=100, pattern_type='random'):
    """
    Create test data with specific patterns.
    
    Args:
        n_samples: Number of samples
        pattern_type: Type of pattern ('random', 'seasonal', 'trend')
        
    Returns:
        DataFrame with patterned data
    """
    timestamps = [datetime.now() - timedelta(hours=i) for i in range(n_samples)]
    
    if pattern_type == 'random':
        values = np.random.randn(n_samples)
    elif pattern_type == 'seasonal':
        # Create seasonal pattern
        values = np.sin(np.arange(n_samples) * 2 * np.pi / 24) + np.random.randn(n_samples) * 0.1
    elif pattern_type == 'trend':
        # Create trending pattern
        values = np.arange(n_samples) * 0.1 + np.random.randn(n_samples) * 0.1
    else:
        values = np.zeros(n_samples)
        
    data = {
        'timestamp': timestamps,
        'value': values
    }
    
    return pd.DataFrame(data)


# ============================================================================
# Performance Fixtures
# ============================================================================

@pytest.fixture
def performance_timer():
    """
    Fixture for timing test execution.
    
    Usage:
        def test_something(performance_timer):
            with performance_timer('operation_name'):
                # code to time
                pass
    """
    import time
    from contextlib import contextmanager
    
    times = {}
    
    @contextmanager
    def timer(name):
        start = time.time()
        yield
        elapsed = time.time() - start
        times[name] = elapsed
        print(f"\n{name} took {elapsed:.4f} seconds")
        
    return timer


# ============================================================================
# Mocking Helpers
# ============================================================================

@pytest.fixture
def mock_snowflake_cursor():
    """Create a mock Snowflake cursor for testing."""
    class MockCursor:
        def __init__(self):
            self.results = []
            
        def execute(self, query):
            return self
            
        def fetchall(self):
            return self.results
            
        def fetchone(self):
            return self.results[0] if self.results else None
            
    return MockCursor()


# ============================================================================
# Validation Helpers
# ============================================================================

def validate_model_metrics(metrics):
    """
    Validate model metrics are within acceptable ranges.
    
    Args:
        metrics: Dictionary of model metrics
        
    Raises:
        AssertionError if metrics are invalid
    """
    assert 'rmse' in metrics, "RMSE metric missing"
    assert 'mae' in metrics, "MAE metric missing"
    
    assert metrics['rmse'] >= 0, "RMSE must be non-negative"
    assert metrics['mae'] >= 0, "MAE must be non-negative"
    
    if 'r2' in metrics:
        assert -1 <= metrics['r2'] <= 1, "R2 must be between -1 and 1"
