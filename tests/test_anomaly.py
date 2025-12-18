# tests/test_anomaly.py
import unittest
import pandas as pd
from src.validation.anomaly_detector import AnomalyDetector

class TestAnomalyDetector(unittest.TestCase):
    def setUp(self):
        self.detector = AnomalyDetector()

    def test_outlier_detection(self):
        # Create DataFrame with one clear outlier in 'value' column
        data = {'id': list(range(1, 12)), 'value': [100]*10 + [1000]}
        df = pd.DataFrame(data)
        mask = self.detector.detect(df, columns=['value'])
        anomalies = df[mask]
        # Should detect the last record (id=11) as an outlier
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies.iloc[0]['id'], 11)

    def test_no_anomaly(self):
        # Data with no outlier
        data = {'id': [1,2,3], 'score': [10, 12, 11]}
        df = pd.DataFrame(data)
        mask = self.detector.detect(df, columns=['score'])
        self.assertEqual(mask.sum(), 0)
