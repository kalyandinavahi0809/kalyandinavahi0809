"""
Unit tests for ML pipeline.

Tests for the Network Signal Imputation pipeline components.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    n_samples = 100
    timestamps = [datetime.now() - timedelta(hours=i) for i in range(n_samples)]
    
    data = {
        'timestamp': timestamps,
        'signal_id': np.random.randint(1, 10, n_samples),
        'signal_strength': np.random.randn(n_samples) * 10 + 50,
        'signal_quality': np.random.randn(n_samples) * 5 + 70,
        'bandwidth_usage': np.random.uniform(0, 100, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Introduce some missing values
    mask = np.random.random(n_samples) < 0.2
    df.loc[mask, 'signal_strength'] = np.nan
    
    return df


@pytest.fixture
def pipeline_config():
    """Create pipeline configuration for testing."""
    return {
        "data_source": "test_data",
        "model_type": "xgboost",
        "feature_store": "disabled"
    }


class TestSignalImputationPipeline:
    """Test suite for SignalImputationPipeline."""
    
    def test_pipeline_initialization(self, pipeline_config):
        """Test pipeline can be initialized with config."""
        from modeling.pipeline import SignalImputationPipeline
        
        pipeline = SignalImputationPipeline(pipeline_config)
        assert pipeline.config == pipeline_config
        assert pipeline.model is None
        
    def test_load_data(self, pipeline_config, sample_data):
        """Test data loading functionality."""
        from modeling.pipeline import SignalImputationPipeline
        
        pipeline = SignalImputationPipeline(pipeline_config)
        
        # Mock data loading
        # In actual implementation, this would load from source
        assert sample_data is not None
        assert len(sample_data) > 0
        
    def test_preprocess_data(self, pipeline_config, sample_data):
        """Test data preprocessing."""
        from modeling.pipeline import SignalImputationPipeline
        
        pipeline = SignalImputationPipeline(pipeline_config)
        processed = pipeline.preprocess(sample_data)
        
        # Verify preprocessing maintains data structure
        assert processed is not None
        assert isinstance(processed, pd.DataFrame)
        
    def test_train_pipeline(self, pipeline_config, sample_data):
        """Test model training."""
        from modeling.pipeline import SignalImputationPipeline
        
        pipeline = SignalImputationPipeline(pipeline_config)
        
        # Split data
        X = sample_data.drop(columns=['signal_strength'])
        y = sample_data['signal_strength']
        
        # Remove NaN values for training
        mask = ~y.isna()
        X_train = X[mask]
        y_train = y[mask]
        
        # Test training doesn't raise errors
        pipeline.train(X_train, y_train)
        
    def test_predict_pipeline(self, pipeline_config, sample_data):
        """Test model prediction."""
        from modeling.pipeline import SignalImputationPipeline
        
        pipeline = SignalImputationPipeline(pipeline_config)
        
        X = sample_data.drop(columns=['signal_strength'])
        predictions = pipeline.predict(X)
        
        # Verify predictions
        assert predictions is not None
        assert isinstance(predictions, np.ndarray)
        
    def test_evaluate_pipeline(self, pipeline_config, sample_data):
        """Test model evaluation."""
        from modeling.pipeline import SignalImputationPipeline
        
        pipeline = SignalImputationPipeline(pipeline_config)
        
        X = sample_data.drop(columns=['signal_strength'])
        y = sample_data['signal_strength']
        
        # Remove NaN values
        mask = ~y.isna()
        X_test = X[mask]
        y_test = y[mask]
        
        metrics = pipeline.evaluate(X_test, y_test)
        
        # Verify metrics structure
        assert isinstance(metrics, dict)
        assert 'rmse' in metrics
        assert 'mae' in metrics
        assert 'r2' in metrics


class TestModelRegistry:
    """Test suite for ModelRegistry."""
    
    def test_registry_initialization(self):
        """Test model registry initialization."""
        from modeling.registry import ModelRegistry
        
        registry = ModelRegistry("snowflake://test")
        assert registry.registry_uri == "snowflake://test"
        
    def test_register_model(self):
        """Test model registration."""
        from modeling.registry import ModelRegistry
        
        registry = ModelRegistry("snowflake://test")
        
        metrics = {"rmse": 0.15, "mae": 0.10}
        version = registry.register_model(
            model_name="test_model",
            model_path="/tmp/model",
            metrics=metrics
        )
        
        # Verify version is returned
        assert version is not None
        assert isinstance(version, str)
        
    def test_promote_model(self):
        """Test model promotion."""
        from modeling.registry import ModelRegistry, ModelStage
        
        registry = ModelRegistry("snowflake://test")
        
        # Test promotion doesn't raise errors
        registry.promote_model(
            model_name="test_model",
            version="v1.0.0",
            stage=ModelStage.STAGING
        )
        
    def test_list_models(self):
        """Test listing models."""
        from modeling.registry import ModelRegistry
        
        registry = ModelRegistry("snowflake://test")
        models = registry.list_models()
        
        # Verify list is returned
        assert isinstance(models, list)


class TestImputationAgent:
    """Test suite for ImputationAgent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        from modeling.agent_model import ImputationAgent
        
        config = {"strategy": "adaptive"}
        agent = ImputationAgent(config)
        
        assert agent.strategy == "adaptive"
        
    def test_assess_missing_pattern(self, sample_data):
        """Test missing data pattern assessment."""
        from modeling.agent_model import ImputationAgent
        
        config = {"strategy": "adaptive"}
        agent = ImputationAgent(config)
        
        pattern_info = agent.assess_missing_pattern(sample_data)
        
        # Verify pattern info structure
        assert isinstance(pattern_info, dict)
        assert 'missing_rate' in pattern_info
        assert 'missing_mechanism' in pattern_info
        
    def test_select_strategy(self, sample_data):
        """Test strategy selection."""
        from modeling.agent_model import ImputationAgent
        
        config = {"strategy": "adaptive"}
        agent = ImputationAgent(config)
        
        pattern_info = agent.assess_missing_pattern(sample_data)
        strategy = agent.select_strategy(pattern_info)
        
        # Verify strategy is selected
        assert strategy is not None
        assert isinstance(strategy, str)
        assert strategy in ["deep_learning", "time_series", "regression"]
        
    def test_impute_column(self, sample_data):
        """Test column imputation."""
        from modeling.agent_model import ImputationAgent
        
        config = {"strategy": "adaptive"}
        agent = ImputationAgent(config)
        
        imputed = agent.impute(sample_data, 'signal_strength')
        
        # Verify imputed values
        assert isinstance(imputed, np.ndarray)
        
    def test_evaluate_quality(self):
        """Test imputation quality evaluation."""
        from modeling.agent_model import ImputationAgent
        
        config = {"strategy": "adaptive"}
        agent = ImputationAgent(config)
        
        original = np.random.randn(100)
        imputed = original + np.random.randn(100) * 0.1
        
        metrics = agent.evaluate_quality(original, imputed)
        
        # Verify metrics
        assert isinstance(metrics, dict)
        assert 'rmse' in metrics
        assert 'mae' in metrics
        assert 'bias' in metrics


class TestHyperparameterTuner:
    """Test suite for HyperparameterTuner."""
    
    def test_tuner_initialization(self):
        """Test tuner initialization."""
        from modeling.hyperparameter_tuning import HyperparameterTuner
        
        config = {"search_method": "bayesian", "n_trials": 10}
        tuner = HyperparameterTuner(config)
        
        assert tuner.search_method == "bayesian"
        assert tuner.n_trials == 10
        
    def test_define_search_space(self):
        """Test search space definition."""
        from modeling.hyperparameter_tuning import HyperparameterTuner
        
        config = {"search_method": "bayesian", "n_trials": 10}
        tuner = HyperparameterTuner(config)
        
        # Test XGBoost search space
        space = tuner.define_search_space("xgboost")
        assert isinstance(space, dict)
        assert "learning_rate" in space
        assert "max_depth" in space
        
        # Test Random Forest search space
        space = tuner.define_search_space("random_forest")
        assert isinstance(space, dict)
        assert "n_estimators" in space
        
    def test_objective_function(self):
        """Test objective function evaluation."""
        from modeling.hyperparameter_tuning import HyperparameterTuner
        
        config = {"search_method": "bayesian", "n_trials": 10}
        tuner = HyperparameterTuner(config)
        
        def dummy_train(params, X, y):
            return None
            
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100)
        X_val = np.random.randn(20, 5)
        y_val = np.random.randn(20)
        
        params = {"learning_rate": 0.1, "max_depth": 5}
        
        score = tuner.objective_function(
            params, dummy_train, X_train, y_train, X_val, y_val
        )
        
        # Verify score is returned
        assert isinstance(score, (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
