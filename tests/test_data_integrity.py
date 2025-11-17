"""
Data integrity tests for Network Signal Imputation pipeline.

Tests data quality, consistency, and validation.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def valid_signal_data():
    """Create valid signal data for testing."""
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
    
    return pd.DataFrame(data)


@pytest.fixture
def invalid_signal_data():
    """Create invalid signal data with quality issues."""
    n_samples = 100
    timestamps = [datetime.now() - timedelta(hours=i) for i in range(n_samples)]
    
    data = {
        'timestamp': timestamps,
        'signal_id': [f'SIGNAL_{i:03d}' for i in range(n_samples)],
        'signal_strength': np.random.uniform(-200, 50, n_samples),  # Invalid range
        'signal_quality': np.random.uniform(-10, 150, n_samples),    # Invalid range
        'bandwidth_usage': np.random.uniform(-5, 105, n_samples),    # Invalid range
        'network_type': np.random.choice(['4G', '5G', 'LTE', 'INVALID'], n_samples)
    }
    
    # Add duplicates
    data_df = pd.DataFrame(data)
    data_df = pd.concat([data_df, data_df.head(10)], ignore_index=True)
    
    return data_df


class TestDataSchema:
    """Test data schema validation."""
    
    def test_required_columns(self, valid_signal_data):
        """Test that all required columns are present."""
        required_columns = [
            'timestamp', 'signal_id', 'signal_strength', 
            'signal_quality', 'bandwidth_usage', 'network_type'
        ]
        
        for col in required_columns:
            assert col in valid_signal_data.columns, f"Missing column: {col}"
            
    def test_column_data_types(self, valid_signal_data):
        """Test column data types are correct."""
        assert pd.api.types.is_datetime64_any_dtype(valid_signal_data['timestamp'])
        assert pd.api.types.is_string_dtype(valid_signal_data['signal_id'])
        assert pd.api.types.is_numeric_dtype(valid_signal_data['signal_strength'])
        assert pd.api.types.is_numeric_dtype(valid_signal_data['signal_quality'])
        assert pd.api.types.is_numeric_dtype(valid_signal_data['bandwidth_usage'])
        assert pd.api.types.is_string_dtype(valid_signal_data['network_type'])
        
    def test_no_empty_dataframe(self, valid_signal_data):
        """Test dataframe is not empty."""
        assert len(valid_signal_data) > 0


class TestDataQuality:
    """Test data quality checks."""
    
    def test_signal_strength_range(self, valid_signal_data):
        """Test signal strength is within valid range."""
        signal_strength = valid_signal_data['signal_strength'].dropna()
        assert signal_strength.min() >= -120
        assert signal_strength.max() <= 0
        
    def test_signal_quality_range(self, valid_signal_data):
        """Test signal quality is within valid range."""
        signal_quality = valid_signal_data['signal_quality'].dropna()
        assert signal_quality.min() >= 0
        assert signal_quality.max() <= 100
        
    def test_bandwidth_usage_range(self, valid_signal_data):
        """Test bandwidth usage is within valid range."""
        bandwidth = valid_signal_data['bandwidth_usage'].dropna()
        assert bandwidth.min() >= 0
        assert bandwidth.max() <= 100
        
    def test_network_type_valid_values(self, valid_signal_data):
        """Test network type contains only valid values."""
        valid_types = ['4G', '5G', 'LTE', '3G']
        network_types = valid_signal_data['network_type'].dropna().unique()
        
        for net_type in network_types:
            assert net_type in valid_types, f"Invalid network type: {net_type}"
            
    def test_missing_data_threshold(self, valid_signal_data):
        """Test missing data is below threshold."""
        max_missing_pct = 30  # 30% threshold
        
        for col in valid_signal_data.columns:
            if col not in ['timestamp', 'signal_id']:
                missing_pct = (valid_signal_data[col].isna().sum() / len(valid_signal_data)) * 100
                assert missing_pct <= max_missing_pct, \
                    f"Column {col} has {missing_pct:.1f}% missing data (threshold: {max_missing_pct}%)"
                    
    def test_no_duplicates(self, valid_signal_data):
        """Test there are no duplicate records."""
        duplicates = valid_signal_data.duplicated(subset=['signal_id', 'timestamp'])
        assert duplicates.sum() == 0, f"Found {duplicates.sum()} duplicate records"
        
    def test_timestamps_ordered(self, valid_signal_data):
        """Test timestamps are properly ordered."""
        # Sort by signal_id and timestamp
        sorted_data = valid_signal_data.sort_values(['signal_id', 'timestamp'])
        
        # Check that timestamps are monotonic within each signal_id
        for signal_id in sorted_data['signal_id'].unique():
            signal_data = sorted_data[sorted_data['signal_id'] == signal_id]
            timestamps = signal_data['timestamp'].values
            
            # Timestamps should be increasing or decreasing
            is_increasing = all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
            is_decreasing = all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1))
            
            assert is_increasing or is_decreasing, \
                f"Timestamps for {signal_id} are not monotonic"


class TestDataConsistency:
    """Test data consistency across the pipeline."""
    
    def test_signal_id_format(self, valid_signal_data):
        """Test signal IDs follow expected format."""
        for signal_id in valid_signal_data['signal_id'].unique():
            assert isinstance(signal_id, str), "Signal ID should be string"
            assert len(signal_id) > 0, "Signal ID should not be empty"
            
    def test_timestamp_recency(self, valid_signal_data):
        """Test timestamps are recent."""
        max_age_days = 90
        oldest_timestamp = valid_signal_data['timestamp'].min()
        age = (datetime.now() - oldest_timestamp).days
        
        assert age <= max_age_days, \
            f"Oldest timestamp is {age} days old (threshold: {max_age_days} days)"
            
    def test_correlation_sanity(self, valid_signal_data):
        """Test feature correlations are reasonable."""
        # Remove missing values
        clean_data = valid_signal_data.dropna()
        
        if len(clean_data) > 10:
            # Calculate correlations
            corr_matrix = clean_data[
                ['signal_strength', 'signal_quality', 'bandwidth_usage']
            ].corr()
            
            # Check that correlations are within reasonable bounds
            for col1 in corr_matrix.columns:
                for col2 in corr_matrix.columns:
                    if col1 != col2:
                        corr_value = corr_matrix.loc[col1, col2]
                        assert -1 <= corr_value <= 1, \
                            f"Correlation between {col1} and {col2} is invalid: {corr_value}"


class TestFeatureEngineering:
    """Test feature engineering transformations."""
    
    def test_standardization(self, valid_signal_data):
        """Test feature standardization."""
        from sklearn.preprocessing import StandardScaler
        
        scaler = StandardScaler()
        signal_strength = valid_signal_data['signal_strength'].dropna().values.reshape(-1, 1)
        
        standardized = scaler.fit_transform(signal_strength)
        
        # Check mean is close to 0 and std is close to 1
        assert abs(standardized.mean()) < 0.1
        assert abs(standardized.std() - 1.0) < 0.1
        
    def test_normalization(self, valid_signal_data):
        """Test feature normalization."""
        from sklearn.preprocessing import MinMaxScaler
        
        scaler = MinMaxScaler()
        bandwidth = valid_signal_data['bandwidth_usage'].dropna().values.reshape(-1, 1)
        
        normalized = scaler.fit_transform(bandwidth)
        
        # Check values are between 0 and 1
        assert normalized.min() >= 0
        assert normalized.max() <= 1
        
    def test_categorical_encoding(self, valid_signal_data):
        """Test categorical variable encoding."""
        network_types = valid_signal_data['network_type'].unique()
        
        # One-hot encoding
        encoded = pd.get_dummies(valid_signal_data['network_type'])
        
        # Check that number of columns matches number of unique values
        assert encoded.shape[1] == len(network_types)
        
        # Check that each row has exactly one 1 (and rest are 0s)
        assert all(encoded.sum(axis=1) == 1)


class TestDataGenerator:
    """Test synthetic data generation."""
    
    def test_generate_synthetic_data(self):
        """Test synthetic data generation."""
        from data.generate_synthetic_data import generate_synthetic_network_data
        
        df = generate_synthetic_network_data(
            num_samples=100,
            num_features=5,
            missing_rate=0.2
        )
        
        # Verify data was generated
        assert len(df) == 100
        assert df.shape[1] >= 7  # timestamp + signal_id + 5 features
        
        # Verify missing data
        missing_rate = df.isna().sum().sum() / (df.shape[0] * df.shape[1])
        assert missing_rate > 0  # Should have some missing data
        

class TestDataValidation:
    """Test data validation functions."""
    
    def test_detect_outliers(self, valid_signal_data):
        """Test outlier detection."""
        signal_strength = valid_signal_data['signal_strength'].dropna()
        
        # Calculate IQR
        q1 = signal_strength.quantile(0.25)
        q3 = signal_strength.quantile(0.75)
        iqr = q3 - q1
        
        # Define outlier bounds
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Count outliers
        outliers = signal_strength[(signal_strength < lower_bound) | (signal_strength > upper_bound)]
        outlier_pct = (len(outliers) / len(signal_strength)) * 100
        
        # Outliers should be less than 10%
        assert outlier_pct < 10, f"Too many outliers: {outlier_pct:.1f}%"
        
    def test_data_completeness(self, valid_signal_data):
        """Test data completeness."""
        # Calculate completeness for each column
        completeness = {}
        for col in valid_signal_data.columns:
            non_null_count = valid_signal_data[col].notna().sum()
            completeness[col] = (non_null_count / len(valid_signal_data)) * 100
            
        # Critical columns should be >70% complete
        critical_columns = ['timestamp', 'signal_id', 'signal_strength']
        for col in critical_columns:
            assert completeness[col] >= 70, \
                f"Column {col} completeness is only {completeness[col]:.1f}%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
