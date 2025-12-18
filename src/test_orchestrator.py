import sys, os
import time
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, precision_recall_fscore_support

# Ensure the 'src' directory is on PYTHONPATH for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from validation.rule_validator import RuleValidator
from validation.anomaly_detector import AnomalyDetector

class TestOrchestrator:
    """
    Advanced test orchestrator for ETL processes with comprehensive validation,
    monitoring, and evaluation capabilities.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logger()
        self.metrics = {}
        self.stage_results = {}
        self.hooks = {
            'pre_extract': [],
            'post_extract': [],
            'pre_transform': [],
            'post_transform': [],
            'pre_load': [],
            'post_load': []
        }
        self.validation_results = {}
        self.evaluation_metrics = {}

    def _setup_logger(self) -> logging.Logger:
        """Set up comprehensive logging."""
        logger = logging.getLogger('TestOrchestrator')
        logger.setLevel(logging.INFO)

        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        log_dir = self.config.get('log_dir', '../logs')
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(
            os.path.join(log_dir, 'test_orchestrator.log')
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def register_hook(self, stage: str, hook_func: Callable) -> None:
        """
        Register a hook function for a specific ETL stage.

        Args:
            stage: One of 'pre_extract', 'post_extract', 'pre_transform',
                   'post_transform', 'pre_load', 'post_load'
            hook_func: Callable that takes (data, context) and returns (data, alerts)
        """
        if stage not in self.hooks:
            raise ValueError(f"Invalid stage: {stage}")
        self.hooks[stage].append(hook_func)
        self.logger.info(f"Registered hook for stage: {stage}")

    def _execute_hooks(self, stage: str, data: Any, context: Dict[str, Any]) -> tuple:
        """Execute all hooks for a given stage."""
        alerts = []
        current_data = data

        for hook in self.hooks[stage]:
            try:
                start_time = time.time()
                result_data, hook_alerts = hook(current_data, context)
                execution_time = time.time() - start_time

                current_data = result_data
                alerts.extend(hook_alerts)

                self.logger.info(f"Hook executed in {execution_time:.3f}s for {stage}")

            except Exception as e:
                alert = {
                    'stage': stage,
                    'type': 'hook_error',
                    'message': f"Hook execution failed: {str(e)}",
                    'severity': 'critical',
                    'timestamp': datetime.now()
                }
                alerts.append(alert)
                self.logger.error(f"Hook failed in {stage}: {str(e)}")

        return current_data, alerts

    def _validate_stage(self, stage: str, data: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run validation logic for a specific stage."""
        validation_config = self.config.get('validation', {}).get(stage, {})

        if not validation_config.get('enabled', True):
            return {'passed': True, 'alerts': [], 'metrics': {}}

        alerts = []
        metrics = {}

        try:
            if stage == 'extract':
                result = self._validate_extract(data, validation_config)
            elif stage == 'transform':
                result = self._validate_transform(data, validation_config)
            elif stage == 'load':
                result = self._validate_load(data, validation_config)
            
            metrics = result.get('metrics', {})
            validation_alerts = result.get('alerts', [])
            alerts.extend(validation_alerts)

            # Check for critical failures
            critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
            if critical_alerts and self.config.get('halt_on_critical', True):
                raise RuntimeError(f"Critical validation failure in {stage}: {critical_alerts}")

        except RuntimeError as e:
            # Re-raise RuntimeError for critical failures when halt_on_critical is True
            if self.config.get('halt_on_critical', True):
                raise
            # Otherwise, convert to alert
            alert = {
                'stage': stage,
                'type': 'validation_error',
                'message': str(e),
                'severity': 'critical',
                'timestamp': datetime.now()
            }
            alerts.append(alert)
        except Exception as e:
            alert = {
                'stage': stage,
                'type': 'validation_error',
                'message': str(e),
                'severity': 'critical',
                'timestamp': datetime.now()
            }
            alerts.append(alert)

        return {
            'passed': len([a for a in alerts if a['severity'] == 'critical']) == 0,
            'alerts': alerts,
            'metrics': metrics
        }

    def _validate_extract(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data."""
        metrics = {
            'record_count': len(data),
            'column_count': len(data.columns),
            'null_percentage': (data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100
        }

        alerts = []

        # Check minimum record count
        min_records = config.get('min_records', 1000)
        if len(data) < min_records:
            alerts.append({
                'stage': 'extract',
                'type': 'data_quality',
                'message': f"Insufficient records: {len(data)} < {min_records}",
                'severity': 'warning',
                'timestamp': datetime.now()
            })

        # Check required columns
        required_cols = config.get('required_columns', [])
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            alerts.append({
                'stage': 'extract',
                'type': 'data_quality',
                'message': f"Missing required columns: {missing_cols}",
                'severity': 'critical',
                'timestamp': datetime.now()
            })

        return {
            'metrics': metrics,
            'alerts': alerts
        }

    def _validate_transform(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate transformed data with anomaly detection."""
        # Define validation rules
        required_cols = config.get('required_columns', ['id', 'report_date', 'transaction_amount',
                                                       'account_type', 'account_balance', 'region'])
        allowed_ranges = config.get('allowed_ranges', {
            'transaction_amount': (0, 15000),
            'account_balance': (0, 70000)
        })
        allowed_categories = config.get('allowed_categories', {
            'account_type': ['Retail', 'Corporate', 'Investment']
        })

        # Rule-based validation
        validator = RuleValidator(required_columns=required_cols,
                                  allowed_ranges=allowed_ranges,
                                  allowed_categories=allowed_categories)
        results = validator.validate(data)
        anomaly_mask_rules = results['anomaly']

        # Statistical anomaly detection
        detector = AnomalyDetector(factor=config.get('iqr_factor', 1.5))
        numeric_cols = config.get('numeric_columns', ['transaction_amount', 'account_balance'])
        anomaly_mask_stats = detector.detect(data, columns=numeric_cols)

        total_anomalies = int(anomaly_mask_rules.sum() + anomaly_mask_stats.sum())

        metrics = {
            'total_records': len(data),
            'rule_based_anomalies': int(anomaly_mask_rules.sum()),
            'statistical_anomalies': int(anomaly_mask_stats.sum()),
            'total_anomalies': total_anomalies,
            'anomaly_percentage': (total_anomalies / len(data)) * 100
        }

        alerts = []

        # Check anomaly thresholds
        max_anomaly_rate = config.get('max_anomaly_rate', 10.0)  # percentage
        if metrics['anomaly_percentage'] > max_anomaly_rate:
            alerts.append({
                'stage': 'transform',
                'type': 'anomaly_detection',
                'message': f"High anomaly rate: {metrics['anomaly_percentage']:.2f}% > {max_anomaly_rate}%",
                'severity': 'warning',
                'timestamp': datetime.now()
            })

        return {
            'metrics': metrics,
            'alerts': alerts
        }

    def _validate_load(self, data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate loaded data."""
        metrics = {}

        if isinstance(data, pd.DataFrame):
            metrics = {
                'loaded_records': len(data),
                'loaded_columns': len(data.columns)
            }
        elif isinstance(data, str):
            # File path
            if os.path.exists(data):
                metrics = {
                    'file_exists': True,
                    'file_size': os.path.getsize(data)
                }
            else:
                metrics = {'file_exists': False}

        alerts = []

        # Check load success
        if not metrics.get('file_exists', True):
            alerts.append({
                'stage': 'load',
                'type': 'load_failure',
                'message': "Load operation failed - output file not found",
                'severity': 'critical',
                'timestamp': datetime.now()
            })

        return {
            'metrics': metrics,
            'alerts': alerts
        }

    def run_etl_test(self, extract_func: Callable, transform_func: Callable,
                    load_func: Callable, **kwargs) -> Dict[str, Any]:
        """
        Run complete ETL test with validation at each stage.

        Args:
            extract_func: Function that extracts data
            transform_func: Function that transforms data
            load_func: Function that loads data
            **kwargs: Additional arguments for ETL functions
        """
        self.logger.info("Starting ETL test orchestration")
        start_time = time.time()

        try:
            # Extract Stage
            self.logger.info("Starting EXTRACT stage")
            extract_start = time.time()

            # Pre-extract hooks
            context = {'stage': 'extract', 'config': self.config}
            _, pre_alerts = self._execute_hooks('pre_extract', None, context)

            # Extract data
            data = extract_func(**kwargs)
            extract_time = time.time() - extract_start

            # Post-extract hooks and validation
            data, post_alerts = self._execute_hooks('post_extract', data, context)
            validation_result = self._validate_stage('extract', data, context)

            self.stage_results['extract'] = {
                'duration': extract_time,
                'alerts': pre_alerts + post_alerts + validation_result['alerts'],
                'metrics': validation_result['metrics'],
                'passed': validation_result['passed']
            }

            # Transform Stage
            self.logger.info("Starting TRANSFORM stage")
            transform_start = time.time()

            # Pre-transform hooks
            context = {'stage': 'transform', 'config': self.config}
            data, pre_alerts = self._execute_hooks('pre_transform', data, context)

            # Transform data
            transformed_data = transform_func(data, **kwargs)
            transform_time = time.time() - transform_start

            # Post-transform hooks and validation
            transformed_data, post_alerts = self._execute_hooks('post_transform', transformed_data, context)
            validation_result = self._validate_stage('transform', transformed_data, context)

            self.stage_results['transform'] = {
                'duration': transform_time,
                'alerts': pre_alerts + post_alerts + validation_result['alerts'],
                'metrics': validation_result['metrics'],
                'passed': validation_result['passed']
            }

            # Load Stage
            self.logger.info("Starting LOAD stage")
            load_start = time.time()

            # Pre-load hooks
            context = {'stage': 'load', 'config': self.config}
            transformed_data, pre_alerts = self._execute_hooks('pre_load', transformed_data, context)

            # Load data
            load_result = load_func(transformed_data, **kwargs)
            load_time = time.time() - load_start

            # Post-load hooks and validation
            load_result, post_alerts = self._execute_hooks('post_load', load_result, context)
            validation_result = self._validate_stage('load', load_result, context)

            self.stage_results['load'] = {
                'duration': load_time,
                'alerts': pre_alerts + post_alerts + validation_result['alerts'],
                'metrics': validation_result['metrics'],
                'passed': validation_result['passed']
            }

            # Calculate overall metrics
            total_time = time.time() - start_time
            self._calculate_overall_metrics(total_time)

            # Generate reports
            self._generate_reports()

            self.logger.info(f"ETL test completed in {total_time:.3f}s")
            return {
                'success': all(stage['passed'] for stage in self.stage_results.values()),
                'total_duration': total_time,
                'stage_results': self.stage_results,
                'evaluation_metrics': self.evaluation_metrics
            }

        except Exception as e:
            self.logger.error(f"ETL test failed: {str(e)}")
            raise

    def _calculate_overall_metrics(self, total_time: float) -> None:
        """Calculate overall evaluation metrics."""
        # Aggregate alerts
        all_alerts = []
        for stage_result in self.stage_results.values():
            all_alerts.extend(stage_result['alerts'])

        # Calculate metrics
        critical_alerts = [a for a in all_alerts if a['severity'] == 'critical']
        warning_alerts = [a for a in all_alerts if a['severity'] == 'warning']

        self.evaluation_metrics = {
            'total_alerts': len(all_alerts),
            'critical_alerts': len(critical_alerts),
            'warning_alerts': len(warning_alerts),
            'total_duration': total_time,
            'stage_durations': {stage: result['duration'] for stage, result in self.stage_results.items()},
            'latency_per_record': total_time / self.stage_results.get('extract', {}).get('metrics', {}).get('record_count', 1)
        }

        # Calculate precision/recall if we have ground truth
        if 'ground_truth' in self.config:
            self._calculate_precision_recall()

    def _calculate_precision_recall(self) -> None:
        """Calculate precision and recall metrics."""
        # This would require ground truth labels
        # For now, we'll use anomaly detection results as predictions
        transform_metrics = self.stage_results.get('transform', {}).get('metrics', {})

        if transform_metrics:
            # Assume anomalies are "positive" predictions
            predicted_positives = transform_metrics.get('total_anomalies', 0)
            total_records = transform_metrics.get('total_records', 1)

            # For demonstration, assume 10% of data has actual anomalies
            actual_positives = int(total_records * 0.1)
            true_positives = min(predicted_positives, actual_positives)

            precision = true_positives / predicted_positives if predicted_positives > 0 else 0
            recall = true_positives / actual_positives if actual_positives > 0 else 0

            self.evaluation_metrics.update({
                'precision': precision,
                'recall': recall,
                'f1_score': 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            })

    def _generate_reports(self) -> None:
        """Generate comprehensive reports and visualizations."""
        log_dir = self.config.get('log_dir', '../logs')
        os.makedirs(log_dir, exist_ok=True)

        # Generate text report
        self._generate_text_report(os.path.join(log_dir, 'test_orchestrator_report.txt'))

        # Generate visualizations
        self._generate_visualizations(os.path.join(log_dir, 'evaluation_plots.png'))

        # Generate HTML dashboard
        self._generate_html_dashboard(os.path.join(log_dir, 'test_dashboard.html'))

    def _generate_text_report(self, output_file: str) -> None:
        """Generate detailed text report."""
        with open(output_file, 'w') as f:
            f.write("ETL Test Orchestrator Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n\n")

            # Overall metrics
            f.write("OVERALL METRICS\n")
            f.write("-" * 20 + "\n")
            for key, value in self.evaluation_metrics.items():
                if isinstance(value, float):
                    f.write(f"{key}: {value:.4f}\n")
                else:
                    f.write(f"{key}: {value}\n")
            f.write("\n")

            # Stage results
            for stage, result in self.stage_results.items():
                f.write(f"{stage.upper()} STAGE\n")
                f.write("-" * (len(stage) + 6) + "\n")
                f.write(f"Duration: {result['duration']:.3f}s\n")
                f.write(f"Passed: {result['passed']}\n")
                f.write(f"Alerts: {len(result['alerts'])}\n")

                if result['metrics']:
                    f.write("Metrics:\n")
                    for key, value in result['metrics'].items():
                        f.write(f"  {key}: {value}\n")

                if result['alerts']:
                    f.write("Alerts:\n")
                    for alert in result['alerts']:
                        f.write(f"  [{alert['severity'].upper()}] {alert['message']}\n")

                f.write("\n")

        self.logger.info(f"Text report generated: {output_file}")

    def _generate_visualizations(self, output_file: str) -> None:
        """Generate evaluation visualizations."""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle('ETL Test Orchestrator Evaluation', fontsize=16)

            # Stage durations
            stages = list(self.stage_results.keys())
            durations = [self.stage_results[s]['duration'] for s in stages]
            axes[0, 0].bar(stages, durations, color='skyblue')
            axes[0, 0].set_title('Stage Execution Times')
            axes[0, 0].set_ylabel('Duration (seconds)')

            # Alert distribution
            alert_counts = {}
            for stage_result in self.stage_results.values():
                for alert in stage_result['alerts']:
                    severity = alert['severity']
                    alert_counts[severity] = alert_counts.get(severity, 0) + 1

            if alert_counts:
                axes[0, 1].pie(alert_counts.values(), labels=alert_counts.keys(),
                              autopct='%1.1f%%', colors=['red', 'orange', 'yellow'])
                axes[0, 1].set_title('Alert Distribution by Severity')

            # Performance metrics
            if 'precision' in self.evaluation_metrics and 'recall' in self.evaluation_metrics:
                metrics = ['precision', 'recall', 'f1_score']
                values = [self.evaluation_metrics.get(m, 0) for m in metrics]
                axes[1, 0].bar(metrics, values, color='lightgreen')
                axes[1, 0].set_title('Performance Metrics')
                axes[1, 0].set_ylim(0, 1)

            # Anomaly detection results (if available)
            transform_metrics = self.stage_results.get('transform', {}).get('metrics', {})
            if transform_metrics:
                anomaly_types = ['rule_based_anomalies', 'statistical_anomalies']
                anomaly_counts = [transform_metrics.get(t, 0) for t in anomaly_types]
                axes[1, 1].bar(anomaly_types, anomaly_counts, color='coral')
                axes[1, 1].set_title('Anomaly Detection Results')
                axes[1, 1].tick_params(axis='x', rotation=45)

            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()

            self.logger.info(f"Visualizations generated: {output_file}")

        except Exception as e:
            self.logger.warning(f"Could not generate visualizations: {str(e)}")

    def _generate_html_dashboard(self, output_file: str) -> None:
        """Generate interactive HTML dashboard."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ETL Test Orchestrator Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ background: #f0f0f0; padding: 10px; margin: 10px; border-radius: 5px; }}
                .stage {{ border: 1px solid #ddd; padding: 15px; margin: 10px; }}
                .alert-critical {{ color: red; }}
                .alert-warning {{ color: orange; }}
                .alert-info {{ color: blue; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>ETL Test Orchestrator Dashboard</h1>
            <p><strong>Generated:</strong> {datetime.now()}</p>

            <h2>Overall Metrics</h2>
            <div style="display: flex; flex-wrap: wrap;">
        """

        for key, value in self.evaluation_metrics.items():
            if isinstance(value, float):
                html_content += f'<div class="metric"><strong>{key}:</strong> {value:.4f}</div>'
            else:
                html_content += f'<div class="metric"><strong>{key}:</strong> {value}</div>'

        html_content += "</div><h2>Stage Results</h2>"

        for stage, result in self.stage_results.items():
            status_color = "green" if result['passed'] else "red"
            html_content += f"""
            <div class="stage">
                <h3 style="color: {status_color};">{stage.upper()} Stage</h3>
                <p><strong>Duration:</strong> {result['duration']:.3f}s</p>
                <p><strong>Status:</strong> {"PASSED" if result['passed'] else "FAILED"}</p>
                <p><strong>Alerts:</strong> {len(result['alerts'])}</p>
            """

            if result['metrics']:
                html_content += "<h4>Metrics</h4><table>"
                for key, value in result['metrics'].items():
                    html_content += f"<tr><td>{key}</td><td>{value}</td></tr>"
                html_content += "</table>"

            if result['alerts']:
                html_content += "<h4>Alerts</h4><table>"
                html_content += "<tr><th>Type</th><th>Severity</th><th>Message</th></tr>"
                for alert in result['alerts']:
                    severity_class = f"alert-{alert['severity']}"
                    html_content += f"""
                    <tr class="{severity_class}">
                        <td>{alert['type']}</td>
                        <td>{alert['severity']}</td>
                        <td>{alert['message']}</td>
                    </tr>
                    """
                html_content += "</table>"

            html_content += "</div>"

        html_content += "</body></html>"

        with open(output_file, 'w') as f:
            f.write(html_content)

        self.logger.info(f"HTML dashboard generated: {output_file}")


# Decorator for ETL stage hooks
def etl_hook(stage: str):
    """
    Decorator to register functions as ETL stage hooks.

    Usage:
        @etl_hook('pre_extract')
        def my_validation_hook(data, context):
            # validation logic
            return data, alerts
    """
    def decorator(func: Callable) -> Callable:
        func._etl_hook_stage = stage
        return func
    return decorator


# Example usage and test functions
def create_sample_extract_func(data_path: str):
    """Factory function to create extract function."""
    def extract():
        df = pd.read_csv(data_path)
        print(f"Extracted {len(df)} records")
        return df
    return extract

def create_sample_transform_func(orchestrator_instance):
    """Factory function to create transform function with orchestrator access."""
    def transform(data):
        # Apply some basic transformation and return the data
        # The orchestrator will handle validation separately
        return data  # Return the transformed data, not metrics
    return transform

def create_sample_load_func(output_path: str):
    """Factory function to create load function."""
    def load(data):
        # For this example, just return the output path
        return output_path
    return load


if __name__ == "__main__":
    # Example configuration
    config = {
        'log_dir': '../logs',
        'halt_on_critical': False,
        'validation': {
            'extract': {
                'enabled': True,
                'min_records': 1000,
                'required_columns': ['id', 'transaction_amount', 'account_balance']
            },
            'transform': {
                'enabled': True,
                'max_anomaly_rate': 15.0,
                'iqr_factor': 1.5
            },
            'load': {
                'enabled': True
            }
        }
    }

    # Create orchestrator
    orchestrator = TestOrchestrator(config)

    # Register example hooks
    @etl_hook('pre_extract')
    def data_quality_check(data, context):
        alerts = []
        if data is None:
            alerts.append({
                'type': 'data_check',
                'message': 'No data provided',
                'severity': 'warning'
            })
        return data, alerts

    # Register the hook
    orchestrator.register_hook('pre_extract', data_quality_check)

    # Create ETL functions
    extract_func = create_sample_extract_func('../data/synthetic_data.csv')
    transform_func = create_sample_transform_func(orchestrator)
    load_func = create_sample_load_func('../data/processed_data.csv')

    # Run the test
    try:
        results = orchestrator.run_etl_test(
            extract_func=extract_func,
            transform_func=transform_func,
            load_func=load_func
        )
        print(f"Test completed successfully: {results['success']}")
        print(f"Total duration: {results['total_duration']:.3f}s")

    except Exception as e:
        print(f"Test failed: {str(e)}")