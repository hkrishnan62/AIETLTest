## AI Powered ETL Testing Validation

An AI-powered ETL testing framework that combines rule-based validation and statistical anomaly detection to help teams
catch data quality issues early, surface potential regulatory risks (AML, structuring, sanctions patterns), and
produce actionable reports for engineers, analysts, and compliance reviewers. Designed for easy integration into
CI pipelines and reproducible testing, it preserves anomalous records so detection logic can be continuously
validated and unit-tested.

## Features

- **Data Source Support**: Processes CSV files and database tables
- **Comprehensive Anomaly Detection**: Rule-based and statistical outlier detection
- **Regulatory Compliance**: Identifies AML, sanctions, and financial crime patterns
- **Detailed Reporting**: Generates HTML reports with categorized findings and severity scoring
- **Testing Framework**: Preserves all anomalies for continuous testing and validation
- **Automated CI/CD**: GitHub Actions workflows for automated testing and reporting

## Project Structure

```
ETL_AnomalyDetection_AI
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
   
   git clone https://github.com/hkrishnan62/ETL_AnomalyDetection_AI.git
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
AIETLTest

A compact, polished ETL testing toolkit with built-in anomaly detection and regulatory validation.

## Why this project

AIETLTest helps teams validate ETL pipelines by detecting statistical and rule-based anomalies, classifying regulatory risks (e.g., AML, structuring), and producing clear reports for debugging, compliance review, and automated testing.

## Highlights

- **Fast setup**: Run CSV or SQLite scans locally.
- **Dual detection**: Rule-based checks + IQR statistical outlier detection.
- **Regulatory focus**: Built-in classifications for AML-like patterns and severity scoring.
- **Test-first friendly**: Preserves anomalies so unit tests can assert detection behavior.
- **Rich reporting**: HTML reports, evaluation plots, and text summaries for CI artifacts.

## Quick Start

1. Create and activate a virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the CSV orchestrator:

```bash
cd src
python orchestrator.py
```

3. (Optional) Prepare and scan the SQLite DB:

```bash
cd src
python setup_db.py
python db_scanner.py
```

Outputs: HTML reports in `logs/` and a preserved dataset in `data/test_data_with_anomalies.csv`.

## Project Layout

```
README.md
data/                       # sample CSVs and generated DB
logs/                       # generated HTML reports & dashboards
src/                        # ETL scripts, orchestrator, DB helpers
src/validation/             # anomaly detector + rule validator
tests/                      # unit tests
requirements.txt
```

## Key Concepts

- **Validation rules**: Required columns and allowed value ranges (e.g., `transaction_amount`, `account_balance`, `account_type`).
- **Statistical detection**: IQR (factor 1.5) to flag outliers for numeric fields.
- **Orchestrator hooks**: `pre_`/`post_` hooks for `extract`, `transform`, and `load` stages to attach custom checks.
- **Reporting**: Severity-tagged alerts and evaluation metrics (precision/recall/F1) for orchestrator runs.

## Testing

Run the test suite with pytest:

```bash
pytest tests/
```

Run an individual test file:

```bash
pytest tests/test_validation.py
```

## For Contributors

- Fork and open a PR.
- Add tests for behavioral changes.
- Keep changes focused and documented.




