# src/validation/anomaly_detector.py
import pandas as pd
from .ml_anomaly import MLAnomaly


class AnomalyDetector:
    """
    Supports simple statistical IQR detection (default) and ML-based methods.

    To preserve backward compatibility the constructor still accepts `factor`.
    """

    def __init__(self, factor=1.5, method=None, ml_params=None):
        self.factor = factor
        self.method = method
        self.ml_params = ml_params or {}
        self.ml_detector = None

    def detect_iqr(self, series):
        if series.empty:
            return pd.Series(dtype=bool)
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - (iqr * self.factor)
        upper_bound = q3 + (iqr * self.factor)
        return (series < lower_bound) | (series > upper_bound)

    def train_ml(self, df, columns=None, method='isolation_forest'):
        """Train an ML-based detector on provided DataFrame and columns.

        Example: `train_ml(df, columns=['x','y'], method='autoencoder')`
        """
        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()
        X = df[columns]
        self.ml_detector = MLAnomaly(method=method, **self.ml_params)
        self.ml_detector.fit(X)
        self.method = method

    def detect(self, df, columns=None):
        """Detect anomalies using either IQR (default) or trained ML detector.

        Returns a boolean Series indexed as `df` where True indicates anomaly.
        """
        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()

        # If ML method specified and detector available, use it
        if self.method in ('isolation_forest', 'autoencoder'):
            if self.ml_detector is None:
                # Lazily train on provided data
                self.train_ml(df, columns=columns, method=self.method)
            X = df[columns]
            mask_arr = self.ml_detector.predict(X)
            return pd.Series(mask_arr, index=df.index)

        # Fallback to IQR
        mask = pd.Series(False, index=df.index)
        for col in columns:
            if col in df.columns:
                mask |= self.detect_iqr(df[col])
        return mask

