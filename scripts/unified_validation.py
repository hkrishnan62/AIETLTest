#!/usr/bin/env python3
"""
UNIFIED VALIDATION SCRIPT
Comprehensive anomaly detection combining Traditional, ML, and Advanced AI techniques

Features:
  - CSV file support
  - SQLite database support
  - Future: Git Secrets support for database credentials (commented out)
  - All detection methods in one script
  - Detailed reporting and comparison
  
Usage:
  python unified_validation.py --csv data/cleaned_data.csv
  python unified_validation.py --db transactions.db --table transactions
  python unified_validation.py --csv data/cleaned_data.csv --compare
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import pandas as pd
import numpy as np
import sqlite3
import time
from datetime import datetime
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Import validation modules
from src.validation.anomaly_detector import AnomalyDetector
from src.validation.rule_validator import RuleValidator
from src.validation.ml_anomaly import MLAnomaly
from src.validation.ai_techniques import (
    FuzzyLogicDetector,
    ExpertSystemDetector,
    TimeSeriesForecastingDetector,
    GeneticAlgorithmDetector,
    EnsembleAIDetector,
    NeuralSymbolicDetector
)

# Check for optional dependencies
TF_AVAILABLE = True
try:
    import tensorflow
except ImportError:
    TF_AVAILABLE = False

# ============================================================================
# FUTURE: Git Secrets support (commented out for now)
# ============================================================================
# To use Git Secrets for database credentials:
# 1. Install: pip install google-cloud-secret-manager
# 2. Set up: gcloud auth application-default login
# 3. Uncomment below and modify get_db_credentials()
#
# from google.cloud import secretmanager
# def get_db_credentials_from_secrets(secret_name: str) -> dict:
#     """Fetch database credentials from Git Secrets / Cloud Secrets Manager"""
#     client = secretmanager.SecretManagerServiceClient()
#     project_id = os.getenv('GCP_PROJECT_ID')
#     name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
#     response = client.access_secret_version(request={"name": name})
#     secret_string = response.payload.data.decode("UTF-8")
#     # Parse as JSON: {"host": "...", "user": "...", "password": "...", "database": "..."}
#     return json.loads(secret_string)
# ============================================================================

# Color codes for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'


class UnifiedValidator:
    """Unified anomaly detection validator combining all techniques"""

    def __init__(self, args):
        self.args = args
        self.results = {}
        self.data_source = None
        self.df = None
        self.numeric_cols = None

    def load_data(self) -> bool:
        """Load data from CSV or database"""
        print(f"\n{BOLD}[1] LOADING DATA{RESET}")
        print("-" * 100)

        if self.args.csv:
            return self._load_csv()
        elif self.args.db:
            return self._load_db()
        else:
            print(f"{RED}✗ No data source specified. Use --csv or --db{RESET}")
            return False

    def _load_csv(self) -> bool:
        """Load data from CSV file"""
        try:
            filepath = self.args.csv
            if not os.path.exists(filepath):
                print(f"{RED}✗ CSV file not found: {filepath}{RESET}")
                return False

            self.df = pd.read_csv(filepath)
            self.data_source = f"CSV: {filepath}"
            print(f"✓ Loaded CSV: {filepath}")
            print(f"  Records: {len(self.df)}")
            print(f"  Columns: {len(self.df.columns)}")
            print(f"  Size: {self.df.memory_usage(deep=True).sum() / 1024:.2f} KB")
            return True
        except Exception as e:
            print(f"{RED}✗ Error loading CSV: {e}{RESET}")
            return False

    def _load_db(self) -> bool:
        """Load data from SQLite database"""
        try:
            db_path = self.args.db
            table_name = self.args.table or "transactions"

            if not os.path.exists(db_path):
                print(f"{RED}✗ Database file not found: {db_path}{RESET}")
                return False

            conn = sqlite3.connect(db_path)
            query = f"SELECT * FROM {table_name}"
            self.df = pd.read_sql_query(query, conn)
            conn.close()

            self.data_source = f"Database: {db_path}, Table: {table_name}"
            print(f"✓ Connected to database: {db_path}")
            print(f"  Table: {table_name}")
            print(f"  Records: {len(self.df)}")
            print(f"  Columns: {len(self.df.columns)}")
            return True
        except Exception as e:
            print(f"{RED}✗ Error loading from database: {e}{RESET}")
            print(f"  {YELLOW}Note: For future database with credentials via Git Secrets,")
            print(f"  uncomment the get_db_credentials_from_secrets() function in this script{RESET}")
            return False

    def prepare_data(self):
        """Prepare data for validation"""
        print(f"\n{BOLD}[2] DATA PREPARATION{RESET}")
        print("-" * 100)

        # Get numeric columns
        self.numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        if not self.numeric_cols:
            print(f"{YELLOW}⚠ No numeric columns found{RESET}")
            return False

        # Use first 4 numeric columns for consistency
        self.numeric_cols = self.numeric_cols[:min(4, len(self.numeric_cols))]
        print(f"✓ Numeric columns identified: {self.numeric_cols}")
        print(f"✓ Using {len(self.numeric_cols)} columns for validation")
        return True

    def run_all_validations(self):
        """Run all validation methods"""
        print(f"\n{BOLD}[3] RUNNING VALIDATIONS{RESET}")
        print("-" * 100)

        validations = [
            ("RULE_BASED", self.validate_rule_based),
            ("IQR", self.validate_iqr),
            ("ISOLATION_FOREST", self.validate_isolation_forest),
            ("KMEANS", self.validate_kmeans),
            ("AUTOENCODER", self.validate_autoencoder),
            ("FUZZY_LOGIC", self.validate_fuzzy_logic),
            ("EXPERT_SYSTEM", self.validate_expert_system),
            ("TIME_SERIES", self.validate_time_series),
            ("GENETIC_ALGORITHM", self.validate_genetic_algorithm),
            ("ENSEMBLE_AI", self.validate_ensemble_ai),
            ("NEURAL_SYMBOLIC", self.validate_neural_symbolic),
        ]

        for name, method in validations:
            try:
                method()
            except Exception as e:
                print(f"{RED}✗ {name}: {str(e)[:60]}{RESET}")
                self.results[name] = {"anomalies": 0, "time": 0, "error": str(e)}

    def validate_rule_based(self):
        """Rule-based validation"""
        start = time.time()
        try:
            required_cols = [self.df.columns[0]]
            validator = RuleValidator(required_columns=required_cols)
            result = validator.validate(self.df)
            anomalies = result['anomaly'].sum()
            elapsed = time.time() - start

            print(f"✓ {BLUE}Rule-Based:{RESET} {anomalies} anomalies ({anomalies/len(self.df)*100:.2f}%) | {elapsed:.4f}s")
            self.results["RULE_BASED"] = {"anomalies": anomalies, "time": elapsed}
        except Exception as e:
            print(f"{YELLOW}⚠ Rule-Based: {str(e)[:50]}{RESET}")

    def validate_iqr(self):
        """IQR statistical baseline"""
        start = time.time()
        detector = AnomalyDetector(factor=1.5)
        mask = detector.detect(self.df, columns=self.numeric_cols)
        elapsed = time.time() - start
        count = mask.sum()

        print(f"✓ {BLUE}IQR Baseline:{RESET} {count} anomalies ({count/len(self.df)*100:.2f}%) | {elapsed:.4f}s")
        self.results["IQR"] = {"anomalies": count, "time": elapsed}

    def validate_isolation_forest(self):
        """Isolation Forest ML"""
        start = time.time()
        detector = AnomalyDetector(method='isolation_forest', ml_params={'contamination': 0.05})
        mask = detector.detect(self.df, columns=self.numeric_cols)
        elapsed = time.time() - start
        count = mask.sum()

        print(f"✓ {BLUE}Isolation Forest:{RESET} {count} anomalies ({count/len(self.df)*100:.2f}%) | {elapsed:.4f}s")
        self.results["ISOLATION_FOREST"] = {"anomalies": count, "time": elapsed}

    def validate_kmeans(self):
        """K-Means Clustering ML"""
        start = time.time()
        detector = AnomalyDetector(method='clustering', ml_params={'contamination': 0.05})
        mask = detector.detect(self.df, columns=self.numeric_cols)
        elapsed = time.time() - start
        count = mask.sum()

        print(f"✓ {BLUE}K-Means Clustering:{RESET} {count} anomalies ({count/len(self.df)*100:.2f}%) | {elapsed:.4f}s")
        self.results["KMEANS"] = {"anomalies": count, "time": elapsed}

    def validate_autoencoder(self):
        """Autoencoder Deep Learning"""
        if not TF_AVAILABLE:
            print(f"{YELLOW}⊘ Autoencoder: TensorFlow not available{RESET}")
            return

        start = time.time()
        detector = AnomalyDetector(method='autoencoder', ml_params={'contamination': 0.05})
        mask = detector.detect(self.df, columns=self.numeric_cols)
        elapsed = time.time() - start
        count = mask.sum()

        print(f"✓ {BLUE}Autoencoder:{RESET} {count} anomalies ({count/len(self.df)*100:.2f}%) | {elapsed:.4f}s")
        self.results["AUTOENCODER"] = {"anomalies": count, "time": elapsed}

    def validate_fuzzy_logic(self):
        """Fuzzy Logic AI"""
        start = time.time()
        detector = AnomalyDetector(method='fuzzy')
        detector.train_ai(self.df, columns=self.numeric_cols, ai_method='fuzzy')
        mask = detector.detect(self.df, columns=self.numeric_cols)
        elapsed = time.time() - start
        count = mask.sum()

        print(f"✓ {BLUE}Fuzzy Logic:{RESET} {count} anomalies ({count/len(self.df)*100:.2f}%) | {elapsed:.4f}s")
        self.results["FUZZY_LOGIC"] = {"anomalies": count, "time": elapsed}

    def validate_expert_system(self):
        """Expert System AI"""
        start = time.time()
        detector = AnomalyDetector(method='expert')
        detector.train_ai(self.df, columns=self.numeric_cols, ai_method='expert')
        mask = detector.detect(self.df, columns=self.numeric_cols)
        elapsed = time.time() - start
        count = mask.sum()

        print(f"✓ {BLUE}Expert System:{RESET} {count} anomalies ({count/len(self.df)*100:.2f}%) | {elapsed:.4f}s")
        self.results["EXPERT_SYSTEM"] = {"anomalies": count, "time": elapsed}

    def validate_time_series(self):
        """Time Series Forecasting AI"""
        start = time.time()
        detector = AnomalyDetector(method='timeseries')
        detector.train_ai(self.df, columns=self.numeric_cols, ai_method='timeseries')
        mask = detector.detect(self.df, columns=self.numeric_cols)
        elapsed = time.time() - start
        count = mask.sum()

        print(f"✓ {BLUE}Time Series:{RESET} {count} anomalies ({count/len(self.df)*100:.2f}%) | {elapsed:.4f}s")
        self.results["TIME_SERIES"] = {"anomalies": count, "time": elapsed}

    def validate_genetic_algorithm(self):
        """Genetic Algorithm AI"""
        start = time.time()
        detector = AnomalyDetector(method='genetic')
        detector.train_ai(self.df, columns=self.numeric_cols, ai_method='genetic')
        mask = detector.detect(self.df, columns=self.numeric_cols)
        elapsed = time.time() - start
        count = mask.sum()

        print(f"✓ {BLUE}Genetic Algorithm:{RESET} {count} anomalies ({count/len(self.df)*100:.2f}%) | {elapsed:.4f}s")
        self.results["GENETIC_ALGORITHM"] = {"anomalies": count, "time": elapsed}

    def validate_ensemble_ai(self):
        """Ensemble AI (all techniques combined)"""
        start = time.time()
        detector = AnomalyDetector(method='ensemble')
        detector.train_ai(self.df, columns=self.numeric_cols, ai_method='ensemble')
        mask = detector.detect(self.df, columns=self.numeric_cols)
        elapsed = time.time() - start
        count = mask.sum()

        print(f"✓ {BLUE}Ensemble AI:{RESET} {count} anomalies ({count/len(self.df)*100:.2f}%) | {elapsed:.4f}s")
        self.results["ENSEMBLE_AI"] = {"anomalies": count, "time": elapsed}

    def validate_neural_symbolic(self):
        """Neural-Symbolic AI"""
        if not TF_AVAILABLE:
            print(f"{YELLOW}⊘ Neural-Symbolic: TensorFlow not available{RESET}")
            return

        start = time.time()
        detector = AnomalyDetector(method='neural_symbolic')
        detector.train_ai(self.df, columns=self.numeric_cols, ai_method='neural_symbolic')
        mask = detector.detect(self.df, columns=self.numeric_cols)
        elapsed = time.time() - start
        count = mask.sum()

        print(f"✓ {BLUE}Neural-Symbolic:{RESET} {count} anomalies ({count/len(self.df)*100:.2f}%) | {elapsed:.4f}s")
        self.results["NEURAL_SYMBOLIC"] = {"anomalies": count, "time": elapsed}

    def print_comparison(self):
        """Print comparison table"""
        if not self.results:
            return

        print(f"\n{BOLD}[4] COMPARISON RESULTS{RESET}")
        print("=" * 100)

        # Categorize methods
        categories = {
            'Traditional': ['RULE_BASED', 'IQR'],
            'Machine Learning': ['ISOLATION_FOREST', 'KMEANS', 'AUTOENCODER'],
            'Advanced AI': ['FUZZY_LOGIC', 'EXPERT_SYSTEM', 'TIME_SERIES', 
                           'GENETIC_ALGORITHM', 'ENSEMBLE_AI', 'NEURAL_SYMBOLIC']
        }

        for category, methods in categories.items():
            print(f"\n{BOLD}● {category}{RESET}")
            print("-" * 100)

            for method in methods:
                if method in self.results:
                    result = self.results[method]
                    anomalies = result.get('anomalies', 0)
                    time_taken = result.get('time', 0)
                    pct = f"{anomalies/len(self.df)*100:.2f}%" if len(self.df) > 0 else "N/A"
                    print(f"  {method:<25} {anomalies:>6} anomalies ({pct:>6}) | {time_taken:>7.4f}s")

    def print_statistics(self):
        """Print summary statistics"""
        if not self.results:
            return

        print(f"\n{BOLD}[5] STATISTICS{RESET}")
        print("=" * 100)

        anomaly_counts = [r['anomalies'] for r in self.results.values() if 'anomalies' in r]
        time_taken = [r['time'] for r in self.results.values() if 'time' in r]

        if anomaly_counts:
            print(f"\n{BOLD}Anomaly Detection:{RESET}")
            print(f"  Average: {YELLOW}{np.mean(anomaly_counts):.1f}{RESET}")
            print(f"  Min (most conservative): {min(anomaly_counts)}")
            print(f"  Max (most sensitive): {max(anomaly_counts)}")
            print(f"  Std Dev: {YELLOW}{np.std(anomaly_counts):.2f}{RESET}")

        if time_taken:
            total_time = sum(time_taken)
            print(f"\n{BOLD}Execution Time:{RESET}")
            print(f"  Total: {YELLOW}{total_time:.2f}s{RESET}")
            print(f"  Average per method: {np.mean(time_taken):.4f}s")
            print(f"  Fastest: {min(time_taken):.4f}s")
            print(f"  Slowest: {max(time_taken):.4f}s")

    def save_report(self):
        """Save validation report (JSON and HTML)"""
        import json
        # JSON report (if requested)
        if self.args.output:
            print(f"\n{BOLD}[6] SAVING REPORT{RESET}")
            print("-" * 100)
            try:
                results_serializable = {}
                for method, data in self.results.items():
                    results_serializable[method] = {
                        'anomalies': int(data.get('anomalies', 0)),
                        'time': float(data.get('time', 0))
                    }
                report_data = {
                    'timestamp': datetime.now().isoformat(),
                    'data_source': self.data_source,
                    'records': int(len(self.df)),
                    'columns': int(len(self.df.columns)),
                    'numeric_columns': self.numeric_cols,
                    'results': results_serializable
                }
                with open(self.args.output, 'w') as f:
                    json.dump(report_data, f, indent=2)
                print(f"✓ Report saved: {self.args.output}")
            except Exception as e:
                print(f"{RED}✗ Error saving report: {e}{RESET}")

        # HTML report (always or if --html-output is specified)
        html_path = getattr(self.args, 'html_output', None)
        if not html_path:
            html_path = 'logs/validation_report.html'
        try:
            os.makedirs(os.path.dirname(html_path), exist_ok=True)
            html = self._generate_html_report()
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✓ HTML report saved: {html_path}")
        except Exception as e:
            print(f"{RED}✗ Error saving HTML report: {e}{RESET}")

    def _generate_html_report(self):
        """Generate a detailed HTML report with sections and styling"""
        style = '''<style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f8f9fa; }
        .container { max-width: 900px; margin: 40px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001; padding: 32px; }
        h1, h2, h3 { color: #2c3e50; }
        table { border-collapse: collapse; width: 100%; margin: 24px 0; }
        th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
        th { background: #e9ecef; }
        tr:nth-child(even) { background: #f2f2f2; }
        .section { margin-bottom: 32px; }
        .summary { background: #e3fcec; padding: 16px; border-radius: 6px; margin-bottom: 24px; }
        .footer { text-align: center; color: #888; margin-top: 40px; font-size: 0.95em; }
        </style>'''
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        summary = f'''
        <div class="summary">
            <b>Validation Run:</b> {timestamp}<br>
            <b>Data Source:</b> {self.data_source}<br>
            <b>Records:</b> {len(self.df)}<br>
            <b>Columns:</b> {len(self.df.columns)}<br>
            <b>Numeric Columns:</b> {', '.join(self.numeric_cols)}
        </div>'''
        # Results Table
        table_rows = ''
        for method, data in self.results.items():
            table_rows += f'<tr><td>{method}</td><td>{data.get("anomalies", 0)}</td><td>{data.get("time", 0):.4f}s</td></tr>'
        results_table = f'''
        <table>
            <tr><th>Method</th><th>Anomalies</th><th>Execution Time</th></tr>
            {table_rows}
        </table>'''
        # Statistics
        anomaly_counts = [r['anomalies'] for r in self.results.values() if 'anomalies' in r]
        time_taken = [r['time'] for r in self.results.values() if 'time' in r]
        stats_html = ''
        if anomaly_counts:
            stats_html += f'<li><b>Average anomalies:</b> {np.mean(anomaly_counts):.1f}</li>'
            stats_html += f'<li><b>Min anomalies:</b> {min(anomaly_counts)}</li>'
            stats_html += f'<li><b>Max anomalies:</b> {max(anomaly_counts)}</li>'
            stats_html += f'<li><b>Std Dev:</b> {np.std(anomaly_counts):.2f}</li>'
        if time_taken:
            stats_html += f'<li><b>Total execution time:</b> {sum(time_taken):.2f}s</li>'
            stats_html += f'<li><b>Average per method:</b> {np.mean(time_taken):.4f}s</li>'
            stats_html += f'<li><b>Fastest:</b> {min(time_taken):.4f}s</li>'
            stats_html += f'<li><b>Slowest:</b> {max(time_taken):.4f}s</li>'
        stats_section = f'<ul>{stats_html}</ul>' if stats_html else ''
        # HTML Layout
        html = f'''
        <html><head><meta charset="utf-8"><title>Anomaly Detection Validation Report</title>{style}</head>
        <body><div class="container">
        <h1>Anomaly Detection Validation Report</h1>
        {summary}
        <div class="section">
            <h2>Detection Results</h2>
            {results_table}
        </div>
        <div class="section">
            <h2>Statistics</h2>
            {stats_section}
        </div>
        <div class="footer">Generated by Unified Validation Script &copy; {datetime.now().year}</div>
        </div></body></html>
        '''
        return html

    def run(self):
        """Run complete validation"""
        print("\n" + "=" * 100)
        print(f"{BOLD}🚀 UNIFIED ANOMALY DETECTION VALIDATION{RESET}".center(100))
        print("=" * 100)
        print(f"Traditional + ML + Advanced AI Techniques")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"TensorFlow: {'✓ Available' if TF_AVAILABLE else '✗ Not available'}")

        # Execute validation pipeline
        if not self.load_data():
            return False

        if not self.prepare_data():
            return False

        self.run_all_validations()
        self.print_comparison()
        self.print_statistics()
        self.save_report()

        print(f"\n" + "=" * 100)
        print(f"{GREEN}✓ VALIDATION COMPLETE{RESET}".center(100))
        print("=" * 100)
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Unified Anomaly Detection Validator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate CSV file
  python unified_validation.py --csv data/cleaned_data.csv

  # Validate database
  python unified_validation.py --db transactions.db --table transactions

  # Validate and save report
  python unified_validation.py --csv data/cleaned_data.csv --output report.json

  # Compare methods (detailed output)
  python unified_validation.py --csv data/cleaned_data.csv --compare
        """
    )

    # Data source arguments
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--csv', type=str, help='Path to CSV file for validation')
    source_group.add_argument('--db', type=str, help='Path to SQLite database file')

    # Optional arguments
    parser.add_argument('--table', type=str, default='transactions',
                       help='Table name in database (default: transactions)')
    parser.add_argument('--output', type=str, help='Output file for JSON report')
    parser.add_argument('--html-output', type=str, help='Output file for HTML report (default: logs/validation_report.html)')
    parser.add_argument('--compare', action='store_true',
                       help='Enable detailed comparison output')

    args = parser.parse_args()

    # Run validation
    validator = UnifiedValidator(args)
    success = validator.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
