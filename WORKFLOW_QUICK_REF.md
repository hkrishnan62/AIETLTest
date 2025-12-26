# Quick Reference: GitHub Actions ML Validation Workflow

## 🎯 One-Minute Setup

### 1. Push to GitHub
```bash
git add .github/workflows/ml-validation-workflow.yml
git commit -m "Add ML validation workflow"
git push origin main
```

### 2. Run Workflow
1. Go to: https://github.com/hkrishnan62/ETL_AnomalyDetection_AI/actions
2. Click **"ML/AI Anomaly Detection Validation"**
3. Click **"Run workflow"**
4. Click **"Run workflow"** again

### 3. View Results
- Watch progress in real-time
- Download results when complete

---

## 📋 Workflow File Location
```
.github/workflows/ml-validation-workflow.yml
```

## 🔧 Trigger Method
**Workflow Dispatch** - On-demand via GitHub UI

## ⏱️ Execution Time
**~6-10 minutes** (depending on dataset size)

---

## 📊 Output Files

| File | Contents |
|------|----------|
| `ml_validation_report.txt` | Full comparison of all 5 detection methods |
| `ml_integration_test.txt` | Verification that methods work with orchestrator |
| `validation_summary.md` | Executive summary with key findings |

---

## 🎯 What Gets Tested

✓ **5 Detection Methods:**
- Rule-based (Structural validation)
- IQR (Statistical baseline)
- Isolation Forest (ML - RECOMMENDED)
- Clustering (K-Means based)
- Autoencoder (Deep learning)

✓ **3 Datasets:**
- cleaned_data.csv (47,600 records)
- synthetic_data.csv (50,003 records)
- test_data_with_anomalies.csv (50,003 records)

✓ **Metrics:**
- Anomaly counts
- Performance times
- Overlap analysis
- Unique detections

---

## 💻 GitHub CLI Command

```bash
# Run workflow
gh workflow run ml-validation-workflow.yml

# View runs
gh run list --workflow=ml-validation-workflow.yml

# Download artifacts
gh run download <run-id> -D ./results
```

---

## 🔗 Useful Links

| Link | Purpose |
|------|---------|
| [Actions Tab](https://github.com/hkrishnan62/ETL_AnomalyDetection_AI/actions) | View all workflows |
| `GITHUB_ACTIONS_SETUP.md` | Detailed setup guide |
| `.github/workflows/README.md` | Workflow documentation |
| `QUICK_START_ML.md` | ML methods guide |

---

## ❓ FAQ

**Q: Do I need to push code each time?**  
A: No, push once. Then run from GitHub UI anytime.

**Q: How long does it take?**  
A: ~6-10 minutes per run.

**Q: Can I choose which dataset?**  
A: Yes! Select from dropdown when running.

**Q: Where are the results?**  
A: Download from Artifacts section after workflow completes.

**Q: Can I run it automatically?**  
A: Yes, edit the workflow to add `push:` or `schedule:` triggers.

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| Workflow not visible | Push `.github/workflows/ml-validation-workflow.yml` to GitHub |
| TensorFlow fails | This is OK, workflow handles it gracefully |
| Artifacts not found | Wait for workflow to complete (green checkmark) |
| Timeout error | Increase `timeout-minutes` in workflow file |

---

## 📝 File Checklist

✓ `.github/workflows/ml-validation-workflow.yml` - Main workflow  
✓ `.github/workflows/README.md` - Workflow docs  
✓ `GITHUB_ACTIONS_SETUP.md` - Setup guide  
✓ `scripts/full_validation_test.py` - Validation script  
✓ `scripts/test_ml_integration.py` - Integration test  
✓ `src/validation/ml_anomaly.py` - ML implementations  

---

## 🎓 Example Output

```
Dataset: synthetic_data.csv (50,003 records)
├─ IQR:              902 anomalies (1.80%)
├─ Isolation Forest: 2,501 anomalies (5.00%)  ← +277%
├─ Autoencoder:     2,501 anomalies (5.00%)
└─ Clustering:        952 anomalies (1.90%)

Performance:
├─ IQR:            0.004s (fastest)
├─ Clustering:     0.01s
├─ Isolation Forest: 0.65s  ← RECOMMENDED
└─ Autoencoder:    20s
```

---

## 🚀 Ready to Go!

1. ✅ Workflow created and documented
2. ✅ Push to GitHub
3. ✅ Run from Actions tab
4. ✅ Download results

**That's it!** 🎉
