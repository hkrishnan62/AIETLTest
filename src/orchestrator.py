import sys, os
# Ensure the 'src' directory is on PYTHONPATH for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from validator.rule_validator import RuleValidator
from validator.anomaly_detector import AnomalyDetector

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
    orchestrator = ETLOrchestrator(data_path="../data/synthetic_data.csv")
    raw_df = orchestrator.extract()
    cleaned_df, metrics = orchestrator.transform(raw_df)
    orchestrator.load(cleaned_df, "../data/cleaned_data.csv")
    print("Metrics:", metrics)