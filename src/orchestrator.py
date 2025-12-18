import sys, os
# Ensure the 'src' directory is on PYTHONPATH for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from validation.rule_validator import RuleValidator
from validation.anomaly_detector import AnomalyDetector

class ETLOrchestrator:
    """
    Simulate ETL process: Extract, Transform (with validation and anomaly detection), and Load.
    """

    def __init__(self, data_path):
        self.data_path = data_path

    def extract(self):
        """Read synthetic data from CSV."""
        df = pd.read_csv(self.data_path)
        print(f"Extracted {len(df)} records from {self.data_path}")
        return df

    def transform(self, df):
        """
        Apply validation rules and anomaly detection, then remove anomalies.
        Returns cleaned DataFrame and summary metrics.
        """
        # Define validation rules
        required_cols = ['id', 'date', 'amount', 'category', 'balance', 'name']
        allowed_ranges = {
            'amount': (0, 1000),   # Acceptable range for amount
            'balance': (0, 1000)   # Acceptable range for balance
        }
        allowed_categories = {
            'category': ['A', 'B', 'C', 'D']  # Valid category codes
        }

        # Rule-based validation
        validator = RuleValidator(required_columns=required_cols,
                                  allowed_ranges=allowed_ranges,
                                  allowed_categories=allowed_categories)
        results = validator.validate(df)
        anomaly_mask_rules = results['anomaly']

        # Statistical anomaly detection on numeric columns
        detector = AnomalyDetector(factor=1.5)
        numeric_cols = ['amount', 'balance']
        anomaly_mask_stats = detector.detect(df, columns=numeric_cols)

        # Combine all anomaly flags (logical OR)
        combined_mask = anomaly_mask_rules | anomaly_mask_stats

        # Compute metrics
        total_records = len(df)
        anomalies_by_rules = int(anomaly_mask_rules.sum())
        anomalies_by_stats = int(anomaly_mask_stats.sum())
        total_anomalies = int(combined_mask.sum())

        # Remove anomalies for cleaned data
        cleaned_df = df[~combined_mask].reset_index(drop=True)
        cleaned_count = len(cleaned_df)

        metrics = {
            'total_records': total_records,
            'anomalies_by_rules': anomalies_by_rules,
            'anomalies_by_stats': anomalies_by_stats,
            'total_anomalies_detected': total_anomalies,
            'cleaned_records': cleaned_count
        }
        return cleaned_df, metrics

    def load(self, df, output_path):
        """Write the cleaned DataFrame to a CSV file."""
        df.to_csv(output_path, index=False)
        print(f"Loaded cleaned data with {len(df)} records to {output_path}")

if __name__ == "__main__":
    # Example execution
    orchestrator = ETLOrchestrator(data_path="data/synthetic_data.csv")
    raw_df = orchestrator.extract()
    cleaned_df, metrics = orchestrator.transform(raw_df)
    orchestrator.load(cleaned_df, "data/cleaned_data.csv")
    print("Metrics:", metrics)
When run (python src/orchestrator.py), this script will read the synthetic data, apply all checks, output data/cleaned_data.csv, and display a summary of metrics.
src/validation/rule_validator.py – Rule Validator
The Rule Validator applies deterministic checks based on business rules:
•	Null checks: Flags rows with missing values in required columns.
•	Duplicate ID check: Flags rows with non-unique id.
•	Range checks: Flags numeric fields outside defined (min, max) ranges.
•	Category checks: Flags invalid categorical codes not in an allowed list.
The validator returns a DataFrame of boolean flags and an overall anomaly flag per row. Here is the rule_validator.py:
# src/validation/rule_validator.py
import pandas as pd

class RuleValidator:
    """
    Applies various validation rules:
    - Null/missing value checks in required fields.
    - Duplicate ID checks.
    - Numeric range checks.
    - Category membership checks.
    """

    def __init__(self, required_columns=None, allowed_ranges=None, allowed_categories=None):
        """
        Initialize with rules:
        - required_columns: list of columns that must not be null.
        - allowed_ranges: dict {column: (min, max)} for numeric range validation.
        - allowed_categories: dict {column: [allowed_values]} for category validation.
        """
        self.required_columns = required_columns or []
        self.allowed_ranges = allowed_ranges or {}
        self.allowed_categories = allowed_categories or {}

    def check_nulls(self, df):
        """Return a mask for rows with nulls in any required column."""
        mask = pd.Series(False, index=df.index)
        for col in self.required_columns:
            if col in df.columns:
                mask |= df[col].isnull()
        return mask

    def check_duplicates(self, df, subset):
        """Return a mask for rows that are duplicates based on subset of columns."""
        return df.duplicated(subset=subset, keep=False)

    def check_ranges(self, df):
        """Return a mask for rows with values outside the allowed numeric ranges."""
        mask = pd.Series(False, index=df.index)
        for col, (min_val, max_val) in self.allowed_ranges.items():
            if col in df.columns:
                mask |= (df[col] < min_val) | (df[col] > max_val)
        return mask

    def check_categories(self, df):
        """Return a mask for rows with invalid category values."""
        mask = pd.Series(False, index=df.index)
        for col, valid_vals in self.allowed_categories.items():
            if col in df.columns:
                mask |= ~df[col].isin(valid_vals)
        return mask

    def validate(self, df):
        """
        Perform all checks and return a DataFrame with boolean flags:
        columns: null_or_missing, duplicate_id, range_violation, invalid_category, and anomaly (any).
        """
        results = pd.DataFrame(index=df.index)
        results['null_or_missing'] = self.check_nulls(df)
        results['duplicate_id'] = self.check_duplicates(df, subset=['id'])
        results['range_violation'] = self.check_ranges(df)
        results['invalid_category'] = self.check_categories(df)
        results['anomaly'] = results.any(axis=1)  # True if any check failed
        return results
