# GitHub Actions Setup Guide

## ✅ ML/AI Validation Workflow is Ready!

Your repository now has a **GitHub Actions workflow** that automatically runs ML/AI anomaly detection validation on-demand.

---

## 🚀 How to Use

### Step 1: Push This Code to GitHub
```bash
git add .github/workflows/ml-validation-workflow.yml
git commit -m "Add ML/AI validation workflow"
git push origin main
```

### Step 2: Trigger the Workflow

#### Option A: GitHub Web Interface (Easiest)
1. Go to your repository: https://github.com/hkrishnan62/ETL_AnomalyDetection_AI
2. Click **Actions** tab at the top
3. Find **"ML/AI Anomaly Detection Validation"** in the left sidebar
4. Click it and select **"Run workflow"**
5. Choose dataset (or leave as "all")
6. Click **"Run workflow"** button
7. Watch the progress and download results

#### Option B: GitHub CLI
```bash
# View available workflows
gh workflow list

# Run the ML validation workflow
gh workflow run ml-validation-workflow.yml
```

---

## 📊 What the Workflow Does

### Automatic Steps:
1. ✅ Checks out your code
2. ✅ Sets up Python 3.12
3. ✅ Installs all dependencies (including TensorFlow)
4. ✅ Runs full validation test (compares all detection methods)
5. ✅ Runs integration test (verifies with orchestrator)
6. ✅ Generates summary report
7. ✅ Uploads results as artifacts

### Generates Reports:
- `ml_validation_report.txt` - Detailed comparison of all methods
- `ml_integration_test.txt` - Integration test results
- `validation_summary.md` - Executive summary

---

## 📈 Expected Results

When the workflow runs, you'll see output like:

```
Dataset: synthetic_data.csv (50,003 records)
├─ IQR:              902 anomalies (1.80%)
├─ Isolation Forest: 2,501 anomalies (5.00%)  ← +277%
├─ Autoencoder:     2,501 anomalies (5.00%)
└─ Clustering:        952 anomalies (1.90%)

Performance:
├─ IQR:            0.004s
├─ Isolation Forest: 0.65s  ← RECOMMENDED
└─ Autoencoder:    20s
```

---

## 📥 Download Results

### From GitHub Web UI:
1. Go to **Actions**
2. Click the latest **"ML/AI Anomaly Detection Validation"** run
3. Scroll to **"Artifacts"** section
4. Click **"ml-validation-reports"**
5. Download the ZIP file

### From Terminal:
```bash
# List recent runs
gh run list --workflow=ml-validation-workflow.yml

# Download artifacts from specific run
gh run download <run-id> -D ./validation-results

# View logs from command line
gh run view <run-id> --log
```

---

## ⚙️ Workflow Configuration

### Current Settings:
- **Trigger:** Manual dispatch only (on-demand)
- **Timeout:** 60 minutes (enough for all tests)
- **Python Version:** 3.12
- **Runner:** Ubuntu-latest

### Optional: Run on Every Push
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
```

### Optional: Run on Pull Requests
Add to the `on:` section:
```yaml
  pull_request:
    branches:
      - main
```

---

## 🔍 Monitoring Workflow Execution

### Real-Time Monitoring:
1. Open **Actions** tab
2. Click the running workflow
3. Watch each step execute
4. See logs in real-time

### After Completion:
- View summary in workflow page
- Download artifacts
- Share results with team

---

## 📋 Workflow Files

```
.github/workflows/
├── ml-validation-workflow.yml   ← NEW: ML validation (on dispatch)
├── etl-workflow.yml             ← Existing: ETL pipeline
├── advanced-testing-workflow.yml ← Existing: Advanced tests
├── db-testing-workflow.yml      ← Existing: Database tests
└── README.md                    ← Documentation (updated)
```

---

## 🆘 Troubleshooting

### Workflow Not Appearing?
- Make sure file is in `.github/workflows/` directory
- Push the changes to GitHub
- Refresh the Actions page

### Workflow Fails on TensorFlow?
- This is expected on some systems
- Logs will show the error
- Check that requirements.txt includes tensorflow

### Reports Not Showing?
- Wait for workflow to complete
- Check the "Artifacts" section
- Reports are available for 90 days

### Need Faster Results?
- Comment out the Autoencoder test (it's slow)
- Edit the workflow and remove the Autoencoder step
- Run only Isolation Forest for quick validation

---

## 📚 Documentation

See detailed workflow documentation at:
- `.github/workflows/README.md` - Full workflow guide
- `QUICK_START_ML.md` - Quick reference for ML methods
- `ML_EXTENSIONS_REPORT.md` - Detailed results and analysis
- `INDEX.md` - Complete project guide

---

## 💡 Next Steps

1. ✅ Push code to GitHub
   ```bash
   git push origin main
   ```

2. ✅ Go to Actions and run the workflow
   - Navigate to: https://github.com/hkrishnan62/ETL_AnomalyDetection_AI/actions

3. ✅ Monitor execution
   - Click "ML/AI Anomaly Detection Validation"
   - Watch the progress

4. ✅ Download and review results
   - Get artifacts from workflow run
   - Share with team

5. ✅ Integrate into your process
   - Run manually as needed
   - Or modify to run automatically

---

## 🎯 Use Cases

### Development:
Run after implementing ML improvements to validate changes

### Testing:
Run before releases to ensure all detection methods work

### Monitoring:
Schedule periodic validation (by adding cron trigger)

### CI/CD:
Run on pull requests to validate new features

### Documentation:
Generate reports for documentation/presentations

---

## 📞 Support

For issues or questions:
1. Check `.github/workflows/README.md`
2. Review workflow logs in GitHub Actions
3. Test locally with `python scripts/full_validation_test.py`

---

**Status:** ✅ Workflow Created and Ready to Use!

Start by pushing code and triggering the workflow from the Actions tab.
