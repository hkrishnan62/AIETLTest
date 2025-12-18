AIETLTest

An AI-powered ETL testing framework for data processing with built-in anomaly detection and regulatory compliance validation.

## Features

- **Data Source Support**: Processes CSV files and database tables
- **Comprehensive Anomaly Detection**: Rule-based and statistical outlier detection
- **Regulatory Compliance**: Identifies AML, sanctions, and financial crime patterns
- **Detailed Reporting**: Generates HTML reports with categorized findings and severity scoring
- **Testing Framework**: Preserves all anomalies for continuous testing and validation
- **Automated CI/CD**: GitHub Actions workflows for automated testing and reporting

## Project Structure

```
AIETLTest/
├── .github/
│   └── workflows/
│       ├── etl-workflow.yml         # GitHub Actions CI/CD for CSV processing
│       ├── db-testing-workflow.yml  # Database anomaly testing workflow
│       └── advanced-testing-workflow.yml # Advanced test orchestrator workflow
├── data/
│   ├── synthetic_data.csv           # Input synthetic dataset
│   ├── test_data_with_anomalies.csv # Output dataset with anomalies preserved (CSV)
│   └── transactions.db              # SQLite database for DB operations
├── logs/
│   ├── csv_anomaly_report.html      # HTML report for CSV processing
│   └── db_anomaly_report.html       # HTML report for database scanning
├── src/
│   ├── orchestrator.py         # Main ETL orchestration script (CSV)
│   ├── db_scanner.py           # Database anomaly scanning script
│   ├── test_orchestrator.py    # Advanced test orchestrator with hooks and evaluation
│   ├── setup_db.py             # Database setup from CSV
│   ├── add_anomalies.py        # Add regulatory anomalies to database
│   └── validation/
│       ├── anomaly_detector.py # Statistical anomaly detection
│       └── rule_validator.py   # Rule-based data validation
├── tests/
│   ├── test_anomaly.py         # Unit tests for anomaly detection
│   ├── test_validation.py      # Unit tests for validation rules
│   └── test_test_orchestrator.py # Tests for advanced test orchestrator
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

1. Clone the repository:
   
   git clone https://github.com/hkrishnan62/AIETLTest.git
   cd AIETLTest
   

2. Create a virtual environment:
   
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
  

3. Install dependencies:
   
   pip install -r requirements.txt
   

## Usage

### CSV Testing Framework

Execute the main orchestrator script for CSV anomaly detection:

```bash
cd src
python orchestrator.py
```

This will:
- Extract data from `../data/synthetic_data.csv`
- Apply comprehensive anomaly detection (rules + statistics)
- Classify findings by regulatory categories (Money Laundering, Structuring, etc.)
- Generate detailed HTML report with severity scoring
- **Preserve all data** including anomalies for testing purposes
- Save complete dataset to `../data/test_data_with_anomalies.csv`

### Database Anomaly Scanning

For database input, first set up the database from CSV:

```bash
cd src
python setup_db.py
```

Then run the database scanner:

```bash
python db_scanner.py
```

This will:
- Connect to the SQLite database at `../data/transactions.db`
- Scan the `transactions` table for anomalies
- Generate detailed HTML report with severity scoring and regulatory classifications
- **Preserve all data** including anomalies for testing purposes
- Save HTML report to `../logs/db_anomaly_report.html`

Validation Rules

The pipeline validates:
- **Required Columns**: `id`, `report_date`, `transaction_amount`, `account_type`, `account_balance`, `region`
- **Numeric Ranges**:
  - `transaction_amount`: 0-15,000
  - `account_balance`: 0-70,000
- **Categories**: `account_type` must be one of `['Retail', 'Corporate', 'Investment']`

### Anomaly Detection

Uses Interquartile Range (IQR) method with a factor of 1.5 to detect statistical outliers in `transaction_amount` and `account_balance` columns.

## Advanced Test Orchestrator

The framework includes a sophisticated test orchestrator (`test_orchestrator.py`) that provides:

### Features

- **Stage-by-Stage Validation**: Triggers validation logic at each ETL stage (Extract, Transform, Load)
- **Modular Hook System**: Extensible middleware-style hooks for custom validation and monitoring
- **Alert Management**: Comprehensive alert logging with severity levels (critical, warning, info)
- **Failure Handling**: Optional halting on critical failures with configurable thresholds
- **Performance Evaluation**: Computes precision, recall, F1-score, and latency metrics
- **Rich Reporting**: Generates text reports, HTML dashboards, and matplotlib visualizations
- **Confusion Matrix**: Visual analysis of anomaly detection performance

### Usage

```python
from src.test_orchestrator import TestOrchestrator, etl_hook

# Configure the orchestrator
config = {
    'log_dir': '../logs',
    'halt_on_critical': False,
    'validation': {
        'extract': {'enabled': True, 'min_records': 1000},
        'transform': {'enabled': True, 'max_anomaly_rate': 10.0},
        'load': {'enabled': True}
    }
}

orchestrator = TestOrchestrator(config)

# Register custom validation hooks
@etl_hook('pre_extract')
def data_quality_check(data, context):
    alerts = []
    # Custom validation logic
    return data, alerts

orchestrator.register_hook('pre_extract', data_quality_check)

# Define ETL functions
def extract_func():
    return pd.read_csv('../data/synthetic_data.csv')

def transform_func(data):
    # Transform logic with anomaly detection
    return data

def load_func(data):
    return '../data/processed_output.csv'

# Run comprehensive ETL test
results = orchestrator.run_etl_test(
    extract_func=extract_func,
    transform_func=transform_func,
    load_func=load_func
)

print(f"Test Success: {results['success']}")
print(f"Total Duration: {results['total_duration']:.3f}s")
```

### Hook System

The orchestrator supports middleware-style hooks for maximum modularity:

```python
# Available hook stages:
# - pre_extract, post_extract
# - pre_transform, post_transform  
# - pre_load, post_load

@orchestrator.etl_hook('pre_transform')
def custom_validation(data, context):
    alerts = []
    # Your custom validation logic
    if some_condition:
        alerts.append({
            'type': 'custom_check',
            'message': 'Custom validation failed',
            'severity': 'warning'
        })
    return data, alerts
```

### Generated Reports

The orchestrator generates comprehensive reports in `../logs/`:

- **`test_orchestrator_report.txt`**: Detailed text report with metrics and alerts
- **`evaluation_plots.png`**: Matplotlib visualizations including confusion matrices
- **`test_dashboard.html`**: Interactive HTML dashboard with stage breakdowns

### Evaluation Metrics

- **Precision/Recall/F1-Score**: Anomaly detection performance metrics
- **Latency Measurements**: Per-stage and total execution times
- **Alert Analytics**: Severity distribution and failure analysis
- **Data Quality Metrics**: Record counts, anomaly rates, validation pass/fail rates

## Running from GitHub Actions

### Option 1: Automatic Execution (Recommended)

The test orchestrator runs automatically as part of the **ETL Pipeline** workflow:

1. **Trigger**: Push to `main` branch or manual dispatch
2. **Jobs**:
   - `run-etl`: Basic ETL processing and unit tests
   - `advanced-etl-testing`: Advanced test orchestrator with comprehensive validation
3. **Artifacts**: Download reports from the Actions run

### Option 2: Dedicated Advanced Testing Workflow

For focused advanced testing, use the **Advanced ETL Testing** workflow:

1. Go to **Actions** tab in your GitHub repository
2. Select **"Advanced ETL Testing"** workflow
3. Click **"Run workflow"**
4. Configure parameters:
   - **Halt on Critical**: Stop execution on critical failures
   - **Max Anomaly Rate**: Threshold for anomaly detection alerts
   - **Log Level**: DEBUG, INFO, WARNING, or ERROR

### Available Workflows

| Workflow | Trigger | Purpose | Artifacts |
|----------|---------|---------|-----------|
| **ETL Pipeline** | Push/PR + Manual | Basic ETL + Unit tests + Advanced testing | `etl-logs`, `test-orchestrator-reports` |
| **Database Anomaly Scanning** | Manual | Database validation only | `db-anomaly-report` |
| **Advanced ETL Testing** | Manual | Comprehensive test orchestrator only | `advanced-test-reports` |

### Viewing Results

1. **Go to Actions tab** in your repository
2. **Click on the workflow run**
3. **Download artifacts** from the bottom of the run page
4. **Open HTML files** in your browser for interactive dashboards

## Testing

Activate the virtual environment and run the test suite:


source /workspaces/.venv/bin/activate  # Or use the full path if not activated
/workspaces/.venv/bin/python -m pytest tests/


Or run individual test files:

/workspaces/.venv/bin/python -m pytest tests/test_validation.py
/workspaces/.venv/bin/python -m pytest tests/test_anomaly.py



## CI/CD

The project includes a GitHub Actions workflow that:
- Runs on pushes and pull requests to `main`
- Sets up Python environment
- Installs dependencies
- Executes the ETL pipeline
- Generates HTML reports
- Uploads logs as artifacts

### Manual Workflow Trigger

You can manually trigger the workflow from the GitHub Actions tab.

### Database Testing Workflow

The project includes a separate workflow for database anomaly testing:

- **Trigger**: Manual (`workflow_dispatch`)
- **Purpose**: Comprehensive database scanning with detailed regulatory anomaly reports
- **Features**: 
  - Detailed anomaly classification (Money Laundering, Structuring, etc.)
  - Severity scoring (Critical, High, Medium, Low)
  - HTML report with categorized findings
  - No data cleaning - preserves anomalies for testing

To run database testing:
1. Go to Actions tab
2. Select "Database Anomaly Testing"
3. Click "Run workflow"
4. Download the `db-anomaly-report` artifact

### Viewing Reports

After workflow execution:
1. Go to the Actions tab
2. Select the latest workflow run
3. Download artifacts from the "Artifacts" section
4. Open `etl_report.html` or `db_anomaly_report.html` in a web browser for formatted reports

## Data Description

The synthetic dataset includes:
- **id**: Unique transaction identifier
- **report_date**: Transaction timestamp
- **transaction_amount**: Transaction value
- **account_balance**: Account balance after transaction
- **risk_score**: Risk assessment score
- **account_age**: Account age in months
- **account_type**: Type of account (`Retail`, `Corporate`, `Investment`)
- **region**: Geographic region (`APAC`, `EU`, `US`)

## Database Support

The project supports SQLite databases for data processing. Use `setup_db.py` to create a database from the CSV file, then use `db_scanner.py` for anomaly detection on database tables. Use `add_anomalies.py` to add various regulatory anomalies (money laundering patterns, structuring, high-risk transactions, etc.) for testing the detection capabilities. The database scanner generates detailed HTML reports with anomaly classifications and severity scoring, making it ideal for compliance testing and regulatory monitoring.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest tests/`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

