AIETLTest

An AI-powered ETL (Extract, Transform, Load) pipeline for data processing with built-in anomaly detection and validation.

Features

- Data Extraction: Reads synthetic financial transaction data from CSV files
- Data Validation: Performs rule-based validation on required columns, ranges, and categories
- Anomaly Detection: Uses statistical methods (IQR-based) to identify outliers in numeric data
- Data Cleaning: Removes detected anomalies and produces cleaned datasets
- Comprehensive Logging: Generates detailed execution logs and HTML reports
- Automated CI/CD: GitHub Actions workflow for automated testing and reporting

## Project Structure

```
AIETLTest/
├── .github/
│   └── workflows/
│       └── etl-workflow.yml    # GitHub Actions CI/CD pipeline
├── data/
│   ├── synthetic_data.csv      # Input synthetic dataset
│   └── cleaned_data.csv        # Output cleaned dataset
├── src/
│   ├── orchestrator.py         # Main ETL orchestration script
│   └── validation/
│       ├── anomaly_detector.py # Statistical anomaly detection
│       └── rule_validator.py   # Rule-based data validation
├── tests/
│   ├── test_anomaly.py         # Unit tests for anomaly detection
│   └── test_validation.py      # Unit tests for validation rules
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

### Running the ETL Pipeline

Execute the main orchestrator script:


cd src
python orchestrator.py


This will:
- Extract data from `../data/synthetic_data.csv`
- Apply validation rules and anomaly detection
- Save cleaned data to `../data/cleaned_data.csv`
- Display processing metrics

Validation Rules

The pipeline validates:
- **Required Columns**: `id`, `report_date`, `transaction_amount`, `account_type`, `account_balance`, `region`
- **Numeric Ranges**:
  - `transaction_amount`: 0-15,000
  - `account_balance`: 0-70,000
- **Categories**: `account_type` must be one of `['Retail', 'Corporate', 'Investment']`

### Anomaly Detection

Uses Interquartile Range (IQR) method with a factor of 1.5 to detect statistical outliers in `transaction_amount` and `account_balance` columns.

## Testing

Activate the virtual environment and run the test suite:

```bash
source /workspaces/.venv/bin/activate  # Or use the full path if not activated
/workspaces/.venv/bin/python -m pytest tests/
```

Or run individual test files:
```bash
/workspaces/.venv/bin/python -m pytest tests/test_validation.py
/workspaces/.venv/bin/python -m pytest tests/test_anomaly.py
```


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

### Viewing Reports

After workflow execution:
1. Go to the Actions tab
2. Select the latest workflow run
3. Download artifacts from the "Artifacts" section
4. Open `etl_report.html` in a web browser for a formatted report

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

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest tests/`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

