# Tests

This directory contains the test suite for the Network Signal Imputation ML pipeline.

## Test Structure

- **test_pipeline.py**: Tests for ML pipeline components
- **test_data_integrity.py**: Data quality and integrity tests
- **test_feature_store.py**: Feature store and feature definition tests
- **conftest.py**: Shared fixtures and test configuration
- **README.md**: This file

## Running Tests

### Run All Tests

```bash
# Run entire test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run tests in parallel
pytest tests/ -n auto
```

### Run Specific Test Files

```bash
# Run pipeline tests only
pytest tests/test_pipeline.py -v

# Run data integrity tests only
pytest tests/test_data_integrity.py -v

# Run feature store tests only
pytest tests/test_feature_store.py -v
```

### Run by Test Markers

```bash
# Run only unit tests
pytest tests/ -m unit -v

# Run only integration tests
pytest tests/ -m integration -v

# Skip slow tests
pytest tests/ -m "not slow" -v

# Run tests requiring Snowflake
pytest tests/ -m requires_snowflake -v
```

### Run Specific Tests

```bash
# Run specific test class
pytest tests/test_pipeline.py::TestSignalImputationPipeline -v

# Run specific test method
pytest tests/test_pipeline.py::TestSignalImputationPipeline::test_pipeline_initialization -v
```

## Test Categories

### Unit Tests
Fast, isolated tests for individual components:
- Model functions
- Feature transformations
- Data validation logic
- Utility functions

### Integration Tests
Tests that verify component interactions:
- Pipeline end-to-end
- Feature store integration
- Model registry integration
- Database operations

### Data Tests
Tests focused on data quality:
- Schema validation
- Data type checking
- Range validation
- Missing data detection
- Duplicate detection

## Test Fixtures

Common fixtures available in `conftest.py`:

### Data Fixtures
- `sample_signal_data`: Sample network signal data
- `sample_training_data`: Training data (X, y)
- `temp_csv_file`: Temporary CSV file with test data

### Configuration Fixtures
- `test_config`: Test environment configuration
- `sample_sizes`: Parametrized sample sizes
- `missing_rates`: Parametrized missing data rates
- `model_types`: Parametrized model types

### Mock Fixtures
- `mock_model`: Mock ML model
- `mock_feature_store`: Mock feature store
- `mock_model_registry`: Mock model registry
- `mock_snowflake_cursor`: Mock Snowflake cursor

## Writing Tests

### Test Structure

```python
import pytest

class TestMyComponent:
    """Test suite for MyComponent."""
    
    def test_initialization(self):
        """Test component initialization."""
        # Arrange
        config = {"param": "value"}
        
        # Act
        component = MyComponent(config)
        
        # Assert
        assert component.config == config
        
    def test_with_fixture(self, sample_signal_data):
        """Test using a fixture."""
        # Arrange
        component = MyComponent()
        
        # Act
        result = component.process(sample_signal_data)
        
        # Assert
        assert result is not None
```

### Using Markers

```python
@pytest.mark.slow
def test_expensive_operation():
    """Test that takes a long time."""
    pass

@pytest.mark.integration
def test_database_integration():
    """Test database integration."""
    pass

@pytest.mark.requires_snowflake
def test_snowflake_query():
    """Test that requires Snowflake connection."""
    pass
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_doubling(input, expected):
    """Test doubling function with multiple inputs."""
    assert double(input) == expected
```

## Test Coverage

### Generate Coverage Report

```bash
# Generate HTML coverage report
pytest tests/ --cov=. --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage Goals
- Overall coverage: > 80%
- Critical paths: > 95%
- New code: 100%

## Continuous Integration

Tests run automatically on:
- Every pull request
- Merges to main branch
- Nightly builds

### CI Configuration

See `.github/workflows/quality_checks.yml` for CI setup.

## Performance Testing

### Timing Tests

```python
def test_performance(performance_timer):
    """Test performance of operation."""
    with performance_timer('my_operation'):
        # Code to time
        result = expensive_operation()
    
    # Assert performance
    assert result is not None
```

### Load Testing

```bash
# Run with larger datasets
pytest tests/ --test-size=large -v
```

## Debugging Tests

### Run with Debug Output

```bash
# Show print statements
pytest tests/ -s

# Show local variables on failure
pytest tests/ -l

# Drop into debugger on failure
pytest tests/ --pdb

# Verbose output
pytest tests/ -vv
```

### Debug Specific Test

```python
# Add breakpoint in test
def test_my_function():
    import pdb; pdb.set_trace()
    result = my_function()
    assert result is not None
```

## Common Issues

### Import Errors

If you encounter import errors:

```bash
# Install package in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Missing Dependencies

```bash
# Install test dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-xdist
```

### Database Connection Errors

Tests requiring Snowflake will skip if connection unavailable:

```python
@pytest.mark.requires_snowflake
def test_snowflake_operation(snowflake_connection):
    """Test will skip if connection fails."""
    pass
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Use descriptive test names
3. **AAA Pattern**: Arrange, Act, Assert
4. **One Assertion**: Test one thing at a time
5. **Fast Tests**: Keep unit tests fast (< 1 second)
6. **Mock External**: Mock external dependencies
7. **Clean Up**: Use fixtures for setup/teardown
8. **Document**: Add docstrings to tests

## Test Data

### Synthetic Data Generation

```python
from data.generate_synthetic_data import generate_synthetic_network_data

# Generate test data
test_data = generate_synthetic_network_data(
    num_samples=100,
    num_features=5,
    missing_rate=0.2
)
```

### Test Data Location

Do not commit test data files to the repository. Use:
- Fixtures to generate data
- Temporary files during tests
- Mock data for unit tests

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure tests pass locally
3. Run full test suite
4. Check test coverage
5. Add integration tests if needed
6. Update this README if needed

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/latest/goodpractices.html)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)
