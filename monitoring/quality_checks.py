"""
Data quality checks for Network Signal Imputation pipeline.

This module implements comprehensive data quality monitoring.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)


class QualityChecker:
    """Comprehensive data quality checking."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize quality checker.
        
        Args:
            config: Quality check configuration
        """
        self.config = config
        self.thresholds = config.get("thresholds", {})
        self.checks_passed = []
        self.checks_failed = []
        
    def check_missing_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Check for missing data in the dataset.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with missing data analysis
        """
        logger.info("Checking missing data...")
        
        missing_stats = {
            "total_records": len(df),
            "missing_by_column": df.isna().sum().to_dict(),
            "missing_percentage": (df.isna().sum() / len(df) * 100).to_dict()
        }
        
        # Check against thresholds
        max_missing_threshold = self.thresholds.get("max_missing_percentage", 30)
        for col, pct in missing_stats["missing_percentage"].items():
            if pct > max_missing_threshold:
                self.checks_failed.append({
                    "check": "missing_data",
                    "column": col,
                    "value": pct,
                    "threshold": max_missing_threshold
                })
            else:
                self.checks_passed.append(f"missing_data_{col}")
                
        return missing_stats
        
    def check_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate data types are correct.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with data type validation results
        """
        logger.info("Checking data types...")
        
        expected_types = self.config.get("expected_types", {})
        type_issues = []
        
        for col, expected_type in expected_types.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if actual_type != expected_type:
                    type_issues.append({
                        "column": col,
                        "expected": expected_type,
                        "actual": actual_type
                    })
                    
        if type_issues:
            self.checks_failed.append({
                "check": "data_types",
                "issues": type_issues
            })
        else:
            self.checks_passed.append("data_types")
            
        return {"type_issues": type_issues}
        
    def check_value_ranges(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Check if values are within expected ranges.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with range validation results
        """
        logger.info("Checking value ranges...")
        
        range_checks = self.config.get("value_ranges", {})
        range_violations = []
        
        for col, (min_val, max_val) in range_checks.items():
            if col in df.columns:
                out_of_range = df[
                    (df[col] < min_val) | (df[col] > max_val)
                ][col].count()
                
                if out_of_range > 0:
                    range_violations.append({
                        "column": col,
                        "min_expected": min_val,
                        "max_expected": max_val,
                        "violations": int(out_of_range)
                    })
                    
        if range_violations:
            self.checks_failed.append({
                "check": "value_ranges",
                "violations": range_violations
            })
        else:
            self.checks_passed.append("value_ranges")
            
        return {"range_violations": range_violations}
        
    def check_duplicates(self, df: pd.DataFrame, key_columns: List[str]) -> Dict[str, Any]:
        """
        Check for duplicate records.
        
        Args:
            df: Input DataFrame
            key_columns: Columns to check for duplicates
            
        Returns:
            Dictionary with duplicate analysis
        """
        logger.info("Checking duplicates...")
        
        duplicates = df[df.duplicated(subset=key_columns, keep=False)]
        duplicate_count = len(duplicates)
        
        threshold = self.thresholds.get("max_duplicates", 0)
        
        if duplicate_count > threshold:
            self.checks_failed.append({
                "check": "duplicates",
                "count": duplicate_count,
                "threshold": threshold
            })
        else:
            self.checks_passed.append("duplicates")
            
        return {
            "duplicate_count": duplicate_count,
            "duplicate_records": duplicates.head(10).to_dict('records')
        }
        
    def check_data_freshness(self, df: pd.DataFrame, timestamp_col: str) -> Dict[str, Any]:
        """
        Check if data is fresh (recent).
        
        Args:
            df: Input DataFrame
            timestamp_col: Name of timestamp column
            
        Returns:
            Dictionary with freshness analysis
        """
        logger.info("Checking data freshness...")
        
        latest_timestamp = df[timestamp_col].max()
        hours_old = (datetime.now() - latest_timestamp).total_seconds() / 3600
        
        max_age_hours = self.thresholds.get("max_data_age_hours", 24)
        
        if hours_old > max_age_hours:
            self.checks_failed.append({
                "check": "data_freshness",
                "hours_old": hours_old,
                "threshold": max_age_hours
            })
        else:
            self.checks_passed.append("data_freshness")
            
        return {
            "latest_timestamp": latest_timestamp,
            "hours_old": hours_old
        }
        
    def check_distribution_shift(
        self,
        df_current: pd.DataFrame,
        df_reference: pd.DataFrame,
        numeric_columns: List[str]
    ) -> Dict[str, Any]:
        """
        Check for distribution shifts in numeric columns.
        
        Args:
            df_current: Current dataset
            df_reference: Reference dataset
            numeric_columns: Columns to check
            
        Returns:
            Dictionary with distribution shift analysis
        """
        logger.info("Checking distribution shifts...")
        
        shifts = []
        
        for col in numeric_columns:
            if col in df_current.columns and col in df_reference.columns:
                current_mean = df_current[col].mean()
                reference_mean = df_reference[col].mean()
                
                if reference_mean != 0:
                    pct_change = abs(
                        (current_mean - reference_mean) / reference_mean * 100
                    )
                    
                    threshold = self.thresholds.get("max_mean_shift_pct", 20)
                    
                    if pct_change > threshold:
                        shifts.append({
                            "column": col,
                            "current_mean": current_mean,
                            "reference_mean": reference_mean,
                            "pct_change": pct_change
                        })
                        
        if shifts:
            self.checks_failed.append({
                "check": "distribution_shift",
                "shifts": shifts
            })
        else:
            self.checks_passed.append("distribution_shift")
            
        return {"distribution_shifts": shifts}
        
    def run_all_checks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run all quality checks.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Comprehensive quality check results
        """
        logger.info("Running all quality checks...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_records": len(df),
            "checks": {}
        }
        
        # Run individual checks
        results["checks"]["missing_data"] = self.check_missing_data(df)
        results["checks"]["data_types"] = self.check_data_types(df)
        results["checks"]["value_ranges"] = self.check_value_ranges(df)
        results["checks"]["duplicates"] = self.check_duplicates(
            df, key_columns=["signal_id", "timestamp"]
        )
        
        if "timestamp" in df.columns:
            results["checks"]["freshness"] = self.check_data_freshness(df, "timestamp")
            
        # Summary
        results["summary"] = {
            "total_checks": len(self.checks_passed) + len(self.checks_failed),
            "passed": len(self.checks_passed),
            "failed": len(self.checks_failed),
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed
        }
        
        logger.info(f"Quality checks complete: {results['summary']}")
        
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    config = {
        "thresholds": {
            "max_missing_percentage": 30,
            "max_duplicates": 0,
            "max_data_age_hours": 24,
            "max_mean_shift_pct": 20
        },
        "value_ranges": {
            "signal_strength": (-120, 0),
            "bandwidth_usage": (0, 100)
        }
    }
    
    checker = QualityChecker(config)
    
    # Example usage
    # df = pd.read_csv("data/signals.csv")
    # results = checker.run_all_checks(df)
    # print(results)
