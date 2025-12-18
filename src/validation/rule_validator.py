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
