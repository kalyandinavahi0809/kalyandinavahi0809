"""
Feature definitions for Network Signal Imputation pipeline.

This module defines all features used in the ML pipeline.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class FeatureType(Enum):
    """Enumeration of feature types."""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TIMESTAMP = "timestamp"


@dataclass
class FeatureDefinition:
    """Definition of a single feature."""
    name: str
    feature_type: FeatureType
    description: str
    source_table: str
    source_column: str
    transformation: Optional[str] = None
    is_required: bool = True


# Define network signal features
SIGNAL_FEATURES = [
    FeatureDefinition(
        name="signal_strength",
        feature_type=FeatureType.NUMERICAL,
        description="Network signal strength in dBm",
        source_table="raw_signals",
        source_column="strength",
        transformation="standardize"
    ),
    FeatureDefinition(
        name="signal_quality",
        feature_type=FeatureType.NUMERICAL,
        description="Signal quality indicator",
        source_table="raw_signals",
        source_column="quality",
        transformation="normalize"
    ),
    FeatureDefinition(
        name="bandwidth_usage",
        feature_type=FeatureType.NUMERICAL,
        description="Bandwidth utilization percentage",
        source_table="raw_signals",
        source_column="bandwidth",
        transformation="standardize"
    ),
    FeatureDefinition(
        name="network_type",
        feature_type=FeatureType.CATEGORICAL,
        description="Type of network (4G, 5G, etc.)",
        source_table="raw_signals",
        source_column="network_type",
        transformation="one_hot_encode"
    ),
]


def get_feature_names() -> List[str]:
    """Get list of all feature names."""
    return [feature.name for feature in SIGNAL_FEATURES]


def get_required_features() -> List[FeatureDefinition]:
    """Get list of required features only."""
    return [feature for feature in SIGNAL_FEATURES if feature.is_required]
