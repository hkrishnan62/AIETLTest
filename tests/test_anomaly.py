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
        anomalies = self.detector.scan(df, context="extract")
        # Should detect the last record (id=11) as an outlier
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]['record_id'], 11)
        self.assertEqual(anomalies[0]['field'], 'value')

    def test_no_anomaly(self):
        # Data with no outlier
        data = {'id': [1,2,3], 'score': [10, 12, 11]}
        df = pd.DataFrame(data)
        anomalies = self.detector.scan(df)
        self.assertEqual(len(anomalies), 0)
