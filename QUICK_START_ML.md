# Quick Start Guide: ML-Based Anomaly Detection

## What Was Added

This repository now has **machine learning-based anomaly detection** in addition to traditional statistical methods.

### New Methods:
1. **Isolation Forest** - Fast, effective multivariate anomaly detection
2. **Autoencoder** - Deep learning approach for complex patterns
3. **Clustering** - K-Means based distance anomaly detection

---

## Quick Demo

### 1. Run Full Validation Test (Compare All Methods)
```bash
cd /workspaces/ETL_AnomalyDetection_AI
python scripts/full_validation_test.py
```

**Shows:**
- IQR vs ML methods side-by-side
- How many anomalies each finds
- Performance comparisons
- Overlapping detections

---

### 2. Run Integration Test (Verify ML Works)
```bash
python scripts/test_ml_integration.py
```

**Verifies:**
- All ML methods work with the orchestrator
- Detected anomalies are reasonable
- Integration is complete

---

### 3. Use in Your Code

#### Option A: Simple API
```python
from src.validation.anomaly_detector import AnomalyDetector
import pandas as pd

df = pd.read_csv('data/cleaned_data.csv')

# Isolation Forest (recommended)
detector = AnomalyDetector(method='isolation_forest')
anomalies = detector.detect(df, columns=['transaction_amount', 'account_balance', 'risk_score', 'account_age'])
print(f"Found {anomalies.sum()} anomalies")
```

#### Option B: With Orchestrator
```python
from src.orchestrator import ETLOrchestrator

orchestrator = ETLOrchestrator('data/cleaned_data.csv')
df = orchestrator.extract()

# Use Isolation Forest instead of default IQR
metrics = orchestrator.transform(df, use_ml=True, ml_method='isolation_forest')
print(f"Anomalies: {metrics['anomalies_by_stats']}")
```

---

## Method Comparison

| Method | Speed | Coverage | Best For |
|--------|-------|----------|----------|
| IQR | ✓ Fastest | Low (univariate) | Baseline, simple outliers |
| Isolation Forest | ✓ Fast | High (multivariate) | **General use (recommended)** |
| Autoencoder | Slow | High (complex patterns) | Non-linear relationships |
| Clustering | ✓ Fast | Medium | Behavioral segmentation |

---

## Key Numbers

On 50K records dataset:
- **IQR:** Found 902 anomalies (1.8%)
- **Isolation Forest:** Found 2,501 anomalies (5.0%) ← **+277% more**
- **Autoencoder:** Found 2,501 anomalies (5.0%) ← **matches IF**
- **Clustering:** Found 952 anomalies (1.9%)

---

## Files to Know

```
src/validation/
  ├── ml_anomaly.py          ← ML implementations
  └── anomaly_detector.py    ← Extended to support ML

src/orchestrator.py           ← Added use_ml parameter

scripts/
  ├── full_validation_test.py     ← Compare all methods
  └── test_ml_integration.py      ← Verify integration

requirements.txt              ← Added tensorflow, scikit-learn
ML_EXTENSIONS_REPORT.md       ← Detailed results & analysis
```

---

## Recommendation

**For production:**
1. Use **Isolation Forest** (speed + accuracy)
2. Combine with **Rule-based validation** (structural checks)
3. Keep **IQR as fallback** (interpretable)

**For maximum coverage:**
- Run all methods
- Use ensemble voting (consensus anomalies)

---

## Troubleshooting

**Q: Autoencoder is slow?**  
A: Yes, it trains a neural network. Use Isolation Forest if speed matters.

**Q: Getting different results on re-runs?**  
A: Set `random_state=42` in detector for reproducibility.

**Q: Too many or too few anomalies?**  
A: Adjust `contamination` parameter (default 0.05 = 5%):
```python
detector = AnomalyDetector(method='isolation_forest', 
                          ml_params={'contamination': 0.10})  # 10% instead
```

---

## Next Steps

1. ✅ Run `scripts/full_validation_test.py` to see comparison
2. ✅ Run `scripts/test_ml_integration.py` to verify setup
3. ✅ Try different methods on your data
4. ✅ Read `ML_EXTENSIONS_REPORT.md` for detailed analysis
5. ✅ Integrate into your ETL pipeline

---

## Support

For details on specific methods, see `ML_EXTENSIONS_REPORT.md`.

All methods are documented in:
- `src/validation/ml_anomaly.py` - Technical implementation
- `scripts/full_validation_test.py` - Usage examples
- `ML_EXTENSIONS_REPORT.md` - Full analysis & results
