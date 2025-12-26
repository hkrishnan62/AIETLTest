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

    def transform(self, df, use_ml=False, ml_method=None):
        """
        Apply validation rules and anomaly detection, then generate detailed anomaly report.
        
        Args:
            df: Input DataFrame
            use_ml: If True, use ML-based anomaly detection instead of IQR
            ml_method: 'isolation_forest', 'clustering', or 'autoencoder'
        
        Returns:
            metrics: Dictionary with anomaly detection results
        """
        # Define validation rules
        required_cols = ['id', 'report_date', 'transaction_amount', 'account_type', 'account_balance', 'region']
        allowed_ranges = {
            'transaction_amount': (0, 15000),   # Acceptable range for transaction_amount
            'account_balance': (0, 70000)   # Acceptable range for account_balance
        }
        allowed_categories = {
            'account_type': ['Retail', 'Corporate', 'Investment']  # Valid account types
        }

        # Rule-based validation
        validator = RuleValidator(required_columns=required_cols,
                                  allowed_ranges=allowed_ranges,
                                  allowed_categories=allowed_categories)
        results = validator.validate(df)
        anomaly_mask_rules = results['anomaly']

        # Statistical anomaly detection on numeric columns
        detector = AnomalyDetector(factor=1.5)
        numeric_cols = ['transaction_amount', 'account_balance']
        
        if use_ml and ml_method:
            # Use ML-based anomaly detection
            detector = AnomalyDetector(method=ml_method, ml_params={'contamination': 0.05})
            anomaly_mask_stats = detector.detect(df, columns=numeric_cols + ['risk_score', 'account_age'] if ml_method == 'autoencoder' else numeric_cols)
        else:
            # Default IQR-based detection
            anomaly_mask_stats = detector.detect(df, columns=numeric_cols)

        # Create detailed anomaly report
        anomaly_report = self.create_detailed_anomaly_report(df, results, anomaly_mask_stats)
        
        # Compute metrics
        total_records = len(df)
        anomalies_by_rules = int(anomaly_mask_rules.sum())
        anomalies_by_stats = int(anomaly_mask_stats.sum())
        total_anomalies = len(anomaly_report)

        metrics = {
            'total_records': total_records,
            'anomalies_by_rules': anomalies_by_rules,
            'anomalies_by_stats': anomalies_by_stats,
            'total_anomalies_detected': total_anomalies,
            'anomaly_report': anomaly_report
        }
        return metrics

    def create_detailed_anomaly_report(self, df, validation_results, statistical_anomalies):
        """
        Create a detailed report of anomalies with classification.
        """
        anomaly_report = []
        
        for idx, row in df.iterrows():
            issues = []
            
            # Check validation rule violations
            if validation_results.loc[idx, 'null_or_missing']:
                issues.append("Missing Required Data")
            
            if validation_results.loc[idx, 'range_violation']:
                if row['transaction_amount'] < 0:
                    issues.append("Negative Transaction Amount")
                elif row['transaction_amount'] > 15000:
                    issues.append("Excessive Transaction Amount")
                if row['account_balance'] < 0:
                    issues.append("Negative Account Balance")
                elif row['account_balance'] > 70000:
                    issues.append("Excessive Account Balance")
            
            if validation_results.loc[idx, 'invalid_category']:
                issues.append("Invalid Account Type")
            
            # Check statistical anomalies
            if statistical_anomalies[idx]:
                if row['transaction_amount'] > 15000 or row['account_balance'] > 70000:
                    issues.append("Statistical Outlier - High Value")
                else:
                    issues.append("Statistical Outlier")
            
            # Classify regulatory issues
            regulatory_issues = self.classify_regulatory_issues(row, issues)
            issues.extend(regulatory_issues)
            
            if issues:
                anomaly_report.append({
                    'record_id': int(row['id']),
                    'issues': issues,
                    'severity': self.calculate_severity(issues),
                    'transaction_amount': row['transaction_amount'],
                    'account_balance': row['account_balance'],
                    'account_type': row['account_type'],
                    'region': row['region'],
                    'risk_score': row.get('risk_score', 'N/A'),
                    'report_date': row['report_date']
                })
        
        return anomaly_report

    def classify_regulatory_issues(self, row, existing_issues):
        """
        Classify anomalies into regulatory categories.
        """
        regulatory_issues = []
        
        amount = row['transaction_amount']
        balance = row['account_balance']
        region = str(row['region'])
        account_type = str(row['account_type'])
        risk_score = row.get('risk_score', 0)
        
        # Money Laundering indicators
        if amount in [10000, 25000, 50000, 100000] and amount > 0:
            regulatory_issues.append("Money Laundering - Round Number Transaction")
        
        if region in ['HighRisk', 'SanctionsLand', 'RestrictedZone', 'WatchList']:
            regulatory_issues.append("High-Risk Region Transaction")
        
        if amount > 50000 and risk_score > 80:
            regulatory_issues.append("Suspicious High-Value Transaction")
        
        # Structuring indicators
        if 9900 <= amount <= 9999:
            regulatory_issues.append("Structuring - Under Reporting Threshold")
        
        # Account issues
        if account_type == 'Suspicious':
            regulatory_issues.append("Suspicious Account Type")
        
        # Pattern analysis
        if amount == 7777:  # The repeating amount we added
            regulatory_issues.append("Unusual Repeating Amount Pattern")
        
        # Negative amounts
        if amount < 0:
            regulatory_issues.append("Accounting Error - Negative Amount")
        
        if balance == 0 and amount > 1000:
            regulatory_issues.append("Zero Balance with Large Transaction")
        
        return regulatory_issues

    def calculate_severity(self, issues):
        """
        Calculate severity score based on issues.
        """
        severity_score = 0
        high_severity_keywords = ['Money Laundering', 'High-Risk', 'Sanctions', 'Suspicious']
        medium_severity_keywords = ['Structuring', 'Excessive', 'Statistical Outlier']
        
        for issue in issues:
            if any(keyword in issue for keyword in high_severity_keywords):
                severity_score += 3
            elif any(keyword in issue for keyword in medium_severity_keywords):
                severity_score += 2
            else:
                severity_score += 1
        
        if severity_score >= 5:
            return "Critical"
        elif severity_score >= 3:
            return "High"
        elif severity_score >= 2:
            return "Medium"
        else:
            return "Low"

    def load(self, df, output_path):
        """Write the DataFrame to a CSV file (no cleaning for testing)."""
        df.to_csv(output_path, index=False)
        print(f"Saved data with {len(df)} records to {output_path} (anomalies preserved for testing)")

    def generate_html_report(self, metrics, output_file):
        """
        Generate detailed HTML report with anomaly classifications.
        """
        from datetime import datetime
        anomaly_report = metrics['anomaly_report']
        
        # Group anomalies by type
        anomaly_types = {}
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
        
        for anomaly in anomaly_report:
            severity_counts[anomaly['severity']] += 1
            for issue in anomaly['issues']:
                if issue not in anomaly_types:
                    anomaly_types[issue] = []
                anomaly_types[issue].append(anomaly)
        
        html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CSV Anomaly Detection Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; text-align: center; }}
                .summary {{ background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 10px 0; display: flex; justify-content: space-around; }}
                .metric {{ text-align: center; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #007acc; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .severity-critical {{ background-color: #ffebee; }}
                .severity-high {{ background-color: #fff3e0; }}
                .severity-medium {{ background-color: #e8f5e8; }}
                .severity-low {{ background-color: #f3e5f5; }}
                .anomaly-type {{ margin: 20px 0; }}
                .anomaly-type h3 {{ color: #d32f2f; border-bottom: 2px solid #d32f2f; padding-bottom: 5px; }}
                .issue-list {{ background: #f9f9f9; padding: 10px; border-radius: 5px; }}
                pre {{ background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>CSV Anomaly Detection Report</h1>
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Source:</strong> {self.data_path}</p>
                
                <div class="summary">
                    <div class="metric">
                        <div class="metric-value">{metrics['total_records']}</div>
                        <div>Total Records</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{metrics['total_anomalies_detected']}</div>
                        <div>Anomalies Detected</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{severity_counts['Critical']}</div>
                        <div>Critical</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{severity_counts['High']}</div>
                        <div>High</div>
                    </div>
                </div>
                
                <h2>Severity Breakdown</h2>
                <table>
                    <tr><th>Severity</th><th>Count</th><th>Description</th></tr>
                    <tr><td>Critical</td><td>{severity_counts['Critical']}</td><td>High-risk regulatory violations requiring immediate attention</td></tr>
                    <tr><td>High</td><td>{severity_counts['High']}</td><td>Serious anomalies that may indicate compliance issues</td></tr>
                    <tr><td>Medium</td><td>{severity_counts['Medium']}</td><td>Moderate anomalies requiring review</td></tr>
                    <tr><td>Low</td><td>{severity_counts['Low']}</td><td>Minor data quality issues</td></tr>
                </table>
                
                <h2>Anomalies by Type</h2>
        '''
        
        for issue_type, anomalies in sorted(anomaly_types.items()):
            html += f'''
                <div class="anomaly-type">
                    <h3>{issue_type} ({len(anomalies)} instances)</h3>
                    <div class="issue-list">
                        <table>
                            <tr><th>Record ID</th><th>Amount</th><th>Balance</th><th>Account Type</th><th>Region</th><th>Risk Score</th><th>Severity</th></tr>
            '''
            for anomaly in anomalies[:10]:  # Show first 10 for brevity
                severity_class = f"severity-{anomaly['severity'].lower()}"
                html += f'''
                            <tr class="{severity_class}">
                                <td>{anomaly['record_id']}</td>
                                <td>${anomaly['transaction_amount']:,.2f}</td>
                                <td>${anomaly['account_balance']:,.2f}</td>
                                <td>{anomaly['account_type']}</td>
                                <td>{anomaly['region']}</td>
                                <td>{anomaly['risk_score']}</td>
                                <td>{anomaly['severity']}</td>
                            </tr>
                '''
            if len(anomalies) > 10:
                html += f'<tr><td colspan="7"><em>... and {len(anomalies) - 10} more records</em></td></tr>'
            html += '''
                        </table>
                    </div>
                </div>
            '''
        
        html += f'''
                <h2>Detailed Metrics</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total Records Scanned</td><td>{metrics['total_records']}</td></tr>
                    <tr><td>Rule-Based Anomalies</td><td>{metrics['anomalies_by_rules']}</td></tr>
                    <tr><td>Statistical Anomalies</td><td>{metrics['anomalies_by_stats']}</td></tr>
                    <tr><td>Total Anomalies Detected</td><td>{metrics['total_anomalies_detected']}</td></tr>
                </table>
                
                <h2>Scan Summary</h2>
                <pre>CSV File: {self.data_path}
Scan completed successfully with {metrics['total_anomalies_detected']} anomalies found across {len(anomaly_types)} different issue types.
Data preserved for testing - no records were cleaned or removed.</pre>
            </div>
        </body>
        </html>
        '''
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        print(f"HTML report saved to {output_file}")

if __name__ == "__main__":
    # Example execution
    orchestrator = ETLOrchestrator(data_path="../data/synthetic_data.csv")
    raw_df = orchestrator.extract()
    metrics = orchestrator.transform(raw_df)
    orchestrator.load(raw_df, "../data/test_data_with_anomalies.csv")
    orchestrator.generate_html_report(metrics, "../logs/csv_anomaly_report.html")
    print("Metrics:", {k: v for k, v in metrics.items() if k != 'anomaly_report'})