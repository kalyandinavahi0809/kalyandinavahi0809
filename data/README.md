# Data Directory

This directory contains scripts and utilities for data generation and management.

## Files

- **generate_synthetic_data.py**: Script to generate synthetic network signal data for testing and development purposes.

## Usage

```python
from data.generate_synthetic_data import generate_synthetic_network_data

# Generate synthetic data
df = generate_synthetic_network_data(
    num_samples=1000,
    num_features=10,
    missing_rate=0.2
)
```

## Data Storage

Production data should be stored in your configured data warehouse (e.g., Snowflake) and not in this directory.
