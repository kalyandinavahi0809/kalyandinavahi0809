"""
Generate synthetic data for Network Signal Imputation ML pipeline.

This module creates synthetic network signal data for testing and development.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_synthetic_network_data(
    num_samples: int = 1000,
    num_features: int = 10,
    missing_rate: float = 0.2
) -> pd.DataFrame:
    """
    Generate synthetic network signal data with missing values.
    
    Args:
        num_samples: Number of data samples to generate
        num_features: Number of signal features
        missing_rate: Proportion of values to mark as missing
        
    Returns:
        DataFrame with synthetic network signal data
    """
    # Generate timestamps
    start_date = datetime.now() - timedelta(days=num_samples)
    timestamps = [start_date + timedelta(hours=i) for i in range(num_samples)]
    
    # Generate feature data
    data = {
        'timestamp': timestamps,
        'signal_id': np.random.randint(1, 100, num_samples)
    }
    
    # Generate signal features
    for i in range(num_features):
        feature_name = f'signal_feature_{i+1}'
        data[feature_name] = np.random.randn(num_samples) * 10 + 50
    
    df = pd.DataFrame(data)
    
    # Introduce missing values
    for col in df.columns:
        if col not in ['timestamp', 'signal_id']:
            mask = np.random.random(num_samples) < missing_rate
            df.loc[mask, col] = np.nan
    
    return df


if __name__ == "__main__":
    # Generate and save synthetic data
    df = generate_synthetic_network_data()
    print(f"Generated {len(df)} samples with {len(df.columns)} columns")
    print(f"Missing values: {df.isna().sum().sum()}")
