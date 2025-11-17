"""
Feature store tests for Network Signal Imputation pipeline.

Tests feature store setup and feature definitions.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def feature_store_config():
    """Create feature store configuration for testing."""
    return {
        "warehouse": "TEST_WH",
        "database": "TEST_DATABASE",
        "schema": "TEST_FEATURE_STORE"
    }


class TestFeatureStoreSetup:
    """Test feature store setup and initialization."""
    
    def test_feature_store_initialization(self, feature_store_config):
        """Test feature store can be initialized."""
        from feature_store.setup_feature_store import FeatureStoreSetup
        
        setup = FeatureStoreSetup(feature_store_config)
        assert setup.config == feature_store_config
        assert setup.connection is None
        
    def test_feature_store_connect(self, feature_store_config):
        """Test feature store connection."""
        from feature_store.setup_feature_store import FeatureStoreSetup
        
        setup = FeatureStoreSetup(feature_store_config)
        
        # Test connection doesn't raise errors
        setup.connect()
        
    def test_feature_group_creation(self, feature_store_config):
        """Test feature group creation."""
        from feature_store.setup_feature_store import FeatureStoreSetup
        
        setup = FeatureStoreSetup(feature_store_config)
        
        # Test feature group creation doesn't raise errors
        setup.create_feature_groups()
        
    def test_materialization_setup(self, feature_store_config):
        """Test feature materialization setup."""
        from feature_store.setup_feature_store import FeatureStoreSetup
        
        setup = FeatureStoreSetup(feature_store_config)
        
        # Test materialization setup doesn't raise errors
        setup.setup_materialization()
        
    def test_full_initialization(self, feature_store_config):
        """Test complete feature store initialization."""
        from feature_store.setup_feature_store import FeatureStoreSetup
        
        setup = FeatureStoreSetup(feature_store_config)
        
        # Test full initialization doesn't raise errors
        setup.initialize()


class TestFeatureDefinitions:
    """Test feature definitions."""
    
    def test_feature_definitions_exist(self):
        """Test feature definitions are defined."""
        from feature_store.feature_definitions import SIGNAL_FEATURES
        
        assert SIGNAL_FEATURES is not None
        assert len(SIGNAL_FEATURES) > 0
        
    def test_feature_definition_structure(self):
        """Test feature definitions have correct structure."""
        from feature_store.feature_definitions import SIGNAL_FEATURES
        
        for feature in SIGNAL_FEATURES:
            assert hasattr(feature, 'name')
            assert hasattr(feature, 'feature_type')
            assert hasattr(feature, 'description')
            assert hasattr(feature, 'source_table')
            assert hasattr(feature, 'source_column')
            
    def test_feature_types(self):
        """Test feature types are valid."""
        from feature_store.feature_definitions import SIGNAL_FEATURES, FeatureType
        
        valid_types = [FeatureType.NUMERICAL, FeatureType.CATEGORICAL, FeatureType.TIMESTAMP]
        
        for feature in SIGNAL_FEATURES:
            assert feature.feature_type in valid_types
            
    def test_get_feature_names(self):
        """Test getting feature names."""
        from feature_store.feature_definitions import get_feature_names
        
        feature_names = get_feature_names()
        
        assert isinstance(feature_names, list)
        assert len(feature_names) > 0
        assert all(isinstance(name, str) for name in feature_names)
        
    def test_get_required_features(self):
        """Test getting required features."""
        from feature_store.feature_definitions import get_required_features
        
        required_features = get_required_features()
        
        assert isinstance(required_features, list)
        assert all(feature.is_required for feature in required_features)
        
    def test_numerical_features_exist(self):
        """Test numerical features are defined."""
        from feature_store.feature_definitions import SIGNAL_FEATURES, FeatureType
        
        numerical_features = [
            f for f in SIGNAL_FEATURES 
            if f.feature_type == FeatureType.NUMERICAL
        ]
        
        assert len(numerical_features) > 0
        
    def test_categorical_features_exist(self):
        """Test categorical features are defined."""
        from feature_store.feature_definitions import SIGNAL_FEATURES, FeatureType
        
        categorical_features = [
            f for f in SIGNAL_FEATURES 
            if f.feature_type == FeatureType.CATEGORICAL
        ]
        
        assert len(categorical_features) > 0


class TestFeatureTransformations:
    """Test feature transformations."""
    
    @pytest.fixture
    def sample_features(self):
        """Create sample feature data."""
        n_samples = 100
        
        data = {
            'signal_strength': np.random.uniform(-120, -30, n_samples),
            'signal_quality': np.random.uniform(0, 100, n_samples),
            'bandwidth_usage': np.random.uniform(0, 100, n_samples),
            'network_type': np.random.choice(['4G', '5G', 'LTE'], n_samples)
        }
        
        return pd.DataFrame(data)
        
    def test_standardize_transformation(self, sample_features):
        """Test standardization transformation."""
        from sklearn.preprocessing import StandardScaler
        
        scaler = StandardScaler()
        standardized = scaler.fit_transform(sample_features[['signal_strength']])
        
        # Check mean ≈ 0 and std ≈ 1
        assert abs(standardized.mean()) < 0.1
        assert abs(standardized.std() - 1.0) < 0.1
        
    def test_normalize_transformation(self, sample_features):
        """Test normalization transformation."""
        from sklearn.preprocessing import MinMaxScaler
        
        scaler = MinMaxScaler()
        normalized = scaler.fit_transform(sample_features[['signal_quality']])
        
        # Check values are in [0, 1]
        assert normalized.min() >= 0
        assert normalized.max() <= 1
        
    def test_one_hot_encoding(self, sample_features):
        """Test one-hot encoding transformation."""
        encoded = pd.get_dummies(sample_features['network_type'], prefix='network')
        
        # Check encoding properties
        assert encoded.shape[0] == len(sample_features)
        assert all(col.startswith('network_') for col in encoded.columns)
        assert all(encoded.sum(axis=1) == 1)  # Each row sums to 1


class TestFeatureValidation:
    """Test feature validation."""
    
    def test_feature_name_uniqueness(self):
        """Test feature names are unique."""
        from feature_store.feature_definitions import get_feature_names
        
        feature_names = get_feature_names()
        
        # Check for duplicates
        assert len(feature_names) == len(set(feature_names)), \
            "Feature names must be unique"
            
    def test_feature_description_not_empty(self):
        """Test feature descriptions are not empty."""
        from feature_store.feature_definitions import SIGNAL_FEATURES
        
        for feature in SIGNAL_FEATURES:
            assert feature.description, \
                f"Feature {feature.name} has empty description"
            assert len(feature.description) > 10, \
                f"Feature {feature.name} description is too short"
                
    def test_source_table_specified(self):
        """Test source table is specified for each feature."""
        from feature_store.feature_definitions import SIGNAL_FEATURES
        
        for feature in SIGNAL_FEATURES:
            assert feature.source_table, \
                f"Feature {feature.name} has no source table"
                
    def test_source_column_specified(self):
        """Test source column is specified for each feature."""
        from feature_store.feature_definitions import SIGNAL_FEATURES
        
        for feature in SIGNAL_FEATURES:
            assert feature.source_column, \
                f"Feature {feature.name} has no source column"


class TestFeatureRetrieval:
    """Test feature retrieval from feature store."""
    
    @pytest.fixture
    def mock_feature_store_data(self):
        """Create mock feature store data."""
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
        
    def test_retrieve_all_features(self, mock_feature_store_data):
        """Test retrieving all features."""
        from feature_store.feature_definitions import get_feature_names
        
        feature_names = get_feature_names()
        
        # Check that all features exist in the data
        for feature_name in feature_names:
            assert feature_name in mock_feature_store_data.columns or \
                   any(feature_name in col for col in mock_feature_store_data.columns)
                   
    def test_retrieve_required_features_only(self, mock_feature_store_data):
        """Test retrieving only required features."""
        from feature_store.feature_definitions import get_required_features
        
        required_features = get_required_features()
        required_names = [f.name for f in required_features]
        
        # Filter to required features
        available_required = [
            name for name in required_names 
            if name in mock_feature_store_data.columns
        ]
        
        assert len(available_required) > 0
        
    def test_feature_freshness(self, mock_feature_store_data):
        """Test feature freshness."""
        latest_timestamp = mock_feature_store_data['timestamp'].max()
        age_hours = (datetime.now() - latest_timestamp).total_seconds() / 3600
        
        # Features should be recent (< 24 hours old)
        assert age_hours < 24, f"Features are {age_hours:.1f} hours old"
        
    def test_feature_completeness(self, mock_feature_store_data):
        """Test feature completeness."""
        # Check for missing values
        for col in mock_feature_store_data.columns:
            if col not in ['timestamp', 'signal_id']:
                missing_pct = (mock_feature_store_data[col].isna().sum() / 
                             len(mock_feature_store_data)) * 100
                             
                # Allow up to 30% missing for features
                assert missing_pct <= 30, \
                    f"Feature {col} has {missing_pct:.1f}% missing values"


class TestFeatureLineage:
    """Test feature lineage tracking."""
    
    def test_feature_has_source_info(self):
        """Test features have source information."""
        from feature_store.feature_definitions import SIGNAL_FEATURES
        
        for feature in SIGNAL_FEATURES:
            # Each feature should have source table and column
            assert feature.source_table is not None
            assert feature.source_column is not None
            
    def test_feature_transformation_documented(self):
        """Test feature transformations are documented."""
        from feature_store.feature_definitions import SIGNAL_FEATURES
        
        for feature in SIGNAL_FEATURES:
            if feature.transformation:
                # Transformation should be a string describing the transformation
                assert isinstance(feature.transformation, str)
                assert len(feature.transformation) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
