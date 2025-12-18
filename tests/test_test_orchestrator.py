import sys, os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

# Ensure the 'src' directory is on PYTHONPATH for imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from test_orchestrator import TestOrchestrator, etl_hook


class TestTestOrchestrator:
    """Test cases for the TestOrchestrator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            'log_dir': '../logs',
            'halt_on_critical': False,
            'validation': {
                'extract': {'enabled': True, 'min_records': 10},
                'transform': {'enabled': True, 'max_anomaly_rate': 50.0},
                'load': {'enabled': True}
            }
        }
        self.orchestrator = TestOrchestrator(self.config)

    def test_initialization(self):
        """Test orchestrator initialization."""
        assert self.orchestrator.config == self.config
        assert self.orchestrator.logger is not None
        assert len(self.orchestrator.hooks) == 6  # All hook stages

    def test_hook_registration(self):
        """Test hook registration functionality."""
        def test_hook(data, context):
            return data, []

        self.orchestrator.register_hook('pre_extract', test_hook)
        assert len(self.orchestrator.hooks['pre_extract']) == 1

        # Test invalid stage
        with pytest.raises(ValueError):
            self.orchestrator.register_hook('invalid_stage', test_hook)

    def test_extract_validation(self):
        """Test extract stage validation."""
        # Create test data
        test_data = pd.DataFrame({
            'id': range(100),
            'transaction_amount': [100] * 100,
            'account_balance': [1000] * 100
        })

        context = {'stage': 'extract', 'config': self.config}
        result = self.orchestrator._validate_stage('extract', test_data, context)

        assert result['passed'] is True
        assert 'record_count' in result['metrics']
        assert result['metrics']['record_count'] == 100

    def test_transform_validation(self):
        """Test transform stage validation."""
        # Create test data with some anomalies
        test_data = pd.DataFrame({
            'id': range(100),
            'report_date': ['2023-01-01'] * 100,
            'transaction_amount': [100] * 95 + [100000] * 5,  # 5 anomalies
            'account_type': ['Retail'] * 100,
            'account_balance': [1000] * 100,
            'region': ['US'] * 100
        })

        context = {'stage': 'transform', 'config': self.config}
        result = self.orchestrator._validate_stage('transform', test_data, context)

        assert result['passed'] is True
        assert 'total_anomalies' in result['metrics']
        assert result['metrics']['total_anomalies'] > 0

    def test_etl_hook_decorator(self):
        """Test ETL hook decorator."""
        @etl_hook('pre_extract')
        def decorated_hook(data, context):
            return data, [{'type': 'test', 'message': 'decorated hook', 'severity': 'info'}]

        assert hasattr(decorated_hook, '_etl_hook_stage')
        assert decorated_hook._etl_hook_stage == 'pre_extract'

    @patch('pandas.read_csv')
    def test_run_etl_test_success(self, mock_read_csv):
        """Test successful ETL test run."""
        # Mock the CSV reading
        mock_read_csv.return_value = pd.DataFrame({
            'id': range(50),
            'transaction_amount': [100] * 50,
            'account_balance': [1000] * 50,
            'report_date': ['2023-01-01'] * 50,
            'account_type': ['Retail'] * 50,
            'region': ['US'] * 50
        })

        # Define simple ETL functions
        def extract_func():
            return pd.read_csv('dummy.csv')

        def transform_func(data):
            return data  # Simple transform

        def load_func(data):
            return 'dummy_output.csv'  # Simple load

        # Run the test
        results = self.orchestrator.run_etl_test(
            extract_func=extract_func,
            transform_func=transform_func,
            load_func=load_func
        )

        assert 'success' in results
        assert 'total_duration' in results
        assert 'stage_results' in results
        assert len(results['stage_results']) == 3  # extract, transform, load

    def test_critical_failure_handling(self):
        """Test handling of critical failures."""
        config_with_halt = self.config.copy()
        config_with_halt['halt_on_critical'] = True

        orchestrator = TestOrchestrator(config_with_halt)

        # Create data that will trigger critical validation failure
        test_data = pd.DataFrame({
            'id': range(5),  # Very few records
            'transaction_amount': [100] * 5,
            'account_balance': [1000] * 5
        })

        # Configure validation to require a missing column (triggers critical alert)
        config_with_halt['validation']['extract']['required_columns'] = ['id', 'missing_column']

        context = {'stage': 'extract', 'config': config_with_halt}

        # This should raise an exception due to critical failure
        with pytest.raises(RuntimeError):
            orchestrator._validate_stage('extract', test_data, context)

    def test_metrics_calculation(self):
        """Test evaluation metrics calculation."""
        # Simulate stage results
        self.orchestrator.stage_results = {
            'extract': {
                'duration': 1.0,
                'alerts': [{'severity': 'warning'}],
                'metrics': {'record_count': 1000},
                'passed': True
            },
            'transform': {
                'duration': 2.0,
                'alerts': [{'severity': 'critical'}],
                'metrics': {'total_anomalies': 50, 'total_records': 1000},
                'passed': False
            },
            'load': {
                'duration': 0.5,
                'alerts': [],
                'metrics': {},
                'passed': True
            }
        }

        self.orchestrator._calculate_overall_metrics(3.5)

        assert 'total_alerts' in self.orchestrator.evaluation_metrics
        assert 'critical_alerts' in self.orchestrator.evaluation_metrics
        assert 'total_duration' in self.orchestrator.evaluation_metrics
        assert self.orchestrator.evaluation_metrics['total_duration'] == 3.5

    def test_report_generation(self):
        """Test report generation functionality."""
        # Set up some test data
        self.orchestrator.evaluation_metrics = {
            'total_alerts': 5,
            'critical_alerts': 1,
            'total_duration': 10.5
        }

        self.orchestrator.stage_results = {
            'extract': {
                'duration': 1.0,
                'alerts': [{'type': 'test', 'severity': 'warning', 'message': 'test alert'}],
                'metrics': {'record_count': 100},
                'passed': True
            }
        }

        # Test text report generation
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            self.orchestrator._generate_text_report('dummy.txt')
            mock_file.write.assert_called()

        # Test HTML dashboard generation
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            self.orchestrator._generate_html_dashboard('dummy.html')
            mock_file.write.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])