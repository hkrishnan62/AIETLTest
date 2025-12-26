#!/usr/bin/env python3
"""Run a quick ML vs IQR anomaly detection comparison on sample CSVs.

Usage: python scripts/ml_demo.py
"""
import os
import sys
from pathlib import Path

# Ensure project root is on path so `src` imports work
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.validation.anomaly_detector import AnomalyDetector


def run_on(path):
    print(f"\nDataset: {path}")
    df = pd.read_csv(path)
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    # prefer to exclude id-like columns
    num_cols = [c for c in num_cols if c.lower() not in ('id', 'index')]
    if not num_cols:
        print('No numeric columns found to analyze.')
        return

    print('Numeric columns used:', num_cols)

    # IQR detector
    iqr_det = AnomalyDetector(factor=1.5)
    mask_iqr = iqr_det.detect(df, columns=num_cols)
    print(f'IQR detected {mask_iqr.sum()} anomalies')

    # Isolation Forest
    if_det = AnomalyDetector(method='isolation_forest')
    mask_if = if_det.detect(df, columns=num_cols)
    print(f'IsolationForest detected {mask_if.sum()} anomalies')

    # Autoencoder (if available)
    try:
        ae_det = AnomalyDetector(method='autoencoder')
        mask_ae = ae_det.detect(df, columns=num_cols)
        print(f'Autoencoder detected {mask_ae.sum()} anomalies')
    except RuntimeError as e:
        print('Autoencoder not available:', e)
        mask_ae = None

    # Comparison
    if mask_ae is None:
        common_if_iqr = (mask_if & mask_iqr).sum()
        print(f'Common (IF & IQR): {common_if_iqr}')
    else:
        common_all = (mask_iqr & mask_if & mask_ae).sum()
        print(f'Common across all methods: {common_all}')

    # Show top anomaly examples from each method
    print('\nSample anomalies by method:')
    if mask_iqr.any():
        print('\nIQR examples:')
        print(df[mask_iqr].head(3).to_string(index=False))
    if mask_if.any():
        print('\nIsolationForest examples:')
        print(df[mask_if].head(3).to_string(index=False))
    if mask_ae is not None and mask_ae.any():
        print('\nAutoencoder examples:')
        print(df[mask_ae].head(3).to_string(index=False))


def main():
    datasets = [
        ROOT / 'data' / 'synthetic_data.csv',
        ROOT / 'data' / 'test_data_with_anomalies.csv',
    ]

    for p in datasets:
        if p.exists():
            run_on(p)
        else:
            print(f'Skipping missing dataset: {p}')


if __name__ == '__main__':
    main()
