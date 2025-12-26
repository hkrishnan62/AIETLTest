# GitHub Actions Workflows

This directory contains automated workflows for the ETL Anomaly Detection project.

## Available Workflows

### 1. ETL Pipeline (`etl-workflow.yml`)
**Trigger:** Push to main, Pull requests, Manual dispatch
**Purpose:** Run unit tests and ETL orchestrator
**Output:** Test results and ETL logs

### 2. Advanced Testing (`advanced-testing-workflow.yml`)
**Trigger:** Push to main, Pull requests, Manual dispatch
**Purpose:** Advanced test suite with detailed reporting
**Output:** Coverage reports and detailed test logs

### 3. Database Testing (`db-testing-workflow.yml`)
**Trigger:** Push to main, Pull requests, Manual dispatch
**Purpose:** Test database scanner and operations
**Output:** Database scan logs and reports

### 4. **ML/AI Anomaly Detection Validation** (`ml-validation-workflow.yml`) ⭐ NEW
**Trigger:** Manual dispatch (workflow_dispatch)
**Purpose:** Run comprehensive ML anomaly detection validation
**Input Options:**
- `all` - Test all datasets (default)
- `cleaned_data.csv` - Test only cleaned data
- `synthetic_data.csv` - Test only synthetic data
- `test_data_with_anomalies.csv` - Test data with anomalies

**What it does:**
1. Installs all dependencies (including TensorFlow, scikit-learn)
2. Runs full validation test comparing all detection methods
3. Runs integration test with orchestrator
4. Generates detailed comparison reports
5. Uploads artifacts with results

**Output Artifacts:**
- `ml_validation_report.txt` - Full comparison of IQR, Isolation Forest, Autoencoder, Clustering
- `ml_integration_test.txt` - Integration test results
- `validation_summary.md` - Summary report

---

## How to Run ML Validation Workflow

### Option 1: GitHub Web UI
1. Go to your repository on GitHub
2. Click **"Actions"** tab
3. Select **"ML/AI Anomaly Detection Validation"** workflow
4. Click **"Run workflow"**
5. Choose dataset (or leave as "all")
6. Click **"Run workflow"**
7. Wait for completion and download artifacts

### Option 2: GitHub CLI
```bash
gh workflow run ml-validation-workflow.yml \
  -f dataset=all
```

### Option 3: Direct
```bash
# Using GitHub CLI
gh workflow run "ML/AI Anomaly Detection Validation.yml"

# Or use the workflow file directly
gh workflow run ml-validation-workflow.yml
```

---

## Workflow Details

### ML Validation Workflow Steps

1. **Checkout code** - Pull latest repository code
2. **Setup Python** - Install Python 3.12
3. **Install dependencies** - Install all required packages
   - pandas, numpy, scikit-learn
   - tensorflow (for Autoencoder)
   - joblib (for model persistence)
4. **Run Full Validation Test**
   - Tests all detection methods
   - Compares results on 3 datasets
   - Generates detailed metrics
5. **Run Integration Test**
   - Verifies ML methods work with orchestrator
   - Checks backward compatibility
6. **Generate Summary Report**
   - Combines all results
   - Creates markdown summary
7. **Upload Artifacts**
   - Makes reports downloadable
   - Available for 90 days

---

## Expected Results

### Validation Report Contains:
- Anomaly counts per method
- Performance comparison table
- Overlap analysis (which anomalies are caught by which methods)
- Unique detections per method
- Key insights and findings

### Example Output:
```
Dataset: synthetic_data.csv (50,003 records)
├─ Rule-based:      2,078 anomalies (4.16%)
├─ IQR:               902 anomalies (1.80%)
├─ Isolation Forest: 2,501 anomalies (5.00%)  ← +277% vs IQR
├─ Clustering:        952 anomalies (1.90%)
└─ Autoencoder:     2,501 anomalies (5.00%)

Performance:
├─ IQR:            0.004s (fastest)
├─ Clustering:     0.01s  (fast)
├─ Isolation Forest: 0.65s (balanced) ← RECOMMENDED
└─ Autoencoder:    20s    (learning)
```

---

## Integration with CI/CD

The ML validation workflow can be integrated into your CI/CD pipeline:

### Run on Every Push (optional modification)
Edit `.github/workflows/ml-validation-workflow.yml` and change:
```yaml
on:
  workflow_dispatch:
```
To:
```yaml
on:
  workflow_dispatch:
  push:
    branches:
      - main
    paths:
      - 'src/validation/**'
      - 'scripts/**'
      - 'requirements.txt'
```

### Run on Pull Requests (optional modification)
```yaml
on:
  workflow_dispatch:
  pull_request:
    branches:
      - main
    paths:
      - 'src/validation/**'
```

---

## Troubleshooting

### Workflow Times Out
- Increase `timeout-minutes` in the workflow
- Or run only specific tests locally

### TensorFlow Installation Fails
- This is expected on some runners
- Workflow includes fallback handling
- Check logs for details

### Artifacts Not Downloaded
- Artifacts are stored for 90 days
- Download from Actions → Workflow Run → Artifacts

### Need Faster Runs
- Comment out Autoencoder test (slowest part)
- Use only Isolation Forest for quick validation

---

## Viewing Results

### In GitHub UI
1. Go to **Actions** → **ML/AI Anomaly Detection Validation**
2. Click the latest run
3. Scroll down to see logs
4. Download artifacts from **Artifacts** section

### In Terminal (GitHub CLI)
```bash
# View workflow runs
gh run list --workflow=ml-validation-workflow.yml

# Download artifacts from latest run
gh run download <run-id> -D ./ml-results
```

---

## Files Involved

- **Workflow:** `.github/workflows/ml-validation-workflow.yml`
- **Test script:** `scripts/full_validation_test.py`
- **Integration test:** `scripts/test_ml_integration.py`
- **Implementation:** `src/validation/ml_anomaly.py`
- **Documentation:** `ML_EXTENSIONS_REPORT.md`, `QUICK_START_ML.md`

---

## Notes

- Workflow requires Python 3.12+
- TensorFlow installation takes ~2 minutes
- Full validation test takes ~3-5 minutes per dataset
- Ubuntu-latest runner used (Linux environment)
- All results are artifacts and can be downloaded

---

For more information:
- See `QUICK_START_ML.md` for quick reference
- See `ML_EXTENSIONS_REPORT.md` for detailed analysis
- See `INDEX.md` for complete documentation
