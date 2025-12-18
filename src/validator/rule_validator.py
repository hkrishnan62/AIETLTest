# src/validation/anomaly_detector.py
import pandas as pd

class AnomalyDetector:
    """
    Performs statistical anomaly detection using the IQR method.
    """

    def __init__(self, factor=1.5):
        self.factor = factor  # Multiplier for IQR (default 1.5)

    def detect_iqr(self, series):
        """
        Detect outliers in a pandas Series using the IQR rule.
        Returns a boolean mask (True for outlier).
        """
        if series.empty:
            return pd.Series(dtype=bool)
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - (iqr * self.factor)
        upper_bound = q3 + (iqr * self.factor)
        return (series < lower_bound) | (series > upper_bound)

    def detect(self, df, columns=None):
        """
        Detect anomalies across specified numeric columns of the DataFrame.
        Returns a boolean mask (True if any column has an outlier).
        """
        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()
        mask = pd.Series(False, index=df.index)
        for col in columns:
            if col in df.columns:
                mask |= self.detect_iqr(df[col])
        return mask
