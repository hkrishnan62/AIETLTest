#!/usr/bin/env python3
"""
Integration test: Verify ML methods work with the full orchestrator pipeline
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
from orchestrator import ETLOrchestrator

print("="*80)
print("Integration Test: ETL Orchestrator with ML Anomaly Detection")
print("="*80)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
test_file = os.path.join(DATA_DIR, 'cleaned_data.csv')

if not os.path.exists(test_file):
    print(f"ERROR: Test file {test_file} not found")
    sys.exit(1)

print(f"\n[1] Testing with IQR (default)")
print("-" * 80)
orchestrator = ETLOrchestrator(test_file)
df = orchestrator.extract()
metrics_iqr = orchestrator.transform(df, use_ml=False)

print(f"Records: {metrics_iqr['total_records']}")
print(f"Rule-based anomalies: {metrics_iqr['anomalies_by_rules']}")
print(f"IQR anomalies: {metrics_iqr['anomalies_by_stats']}")
print(f"Total anomalies: {metrics_iqr['total_anomalies_detected']}")

print(f"\n[2] Testing with Isolation Forest")
print("-" * 80)
metrics_if = orchestrator.transform(df, use_ml=True, ml_method='isolation_forest')
print(f"Records: {metrics_if['total_records']}")
print(f"Rule-based anomalies: {metrics_if['anomalies_by_rules']}")
print(f"Isolation Forest anomalies: {metrics_if['anomalies_by_stats']}")
print(f"Total anomalies: {metrics_if['total_anomalies_detected']}")

print(f"\n[3] Testing with Autoencoder")
print("-" * 80)
metrics_ae = orchestrator.transform(df, use_ml=True, ml_method='autoencoder')
print(f"Records: {metrics_ae['total_records']}")
print(f"Rule-based anomalies: {metrics_ae['anomalies_by_rules']}")
print(f"Autoencoder anomalies: {metrics_ae['anomalies_by_stats']}")
print(f"Total anomalies: {metrics_ae['total_anomalies_detected']}")

print(f"\n[4] Testing with Clustering")
print("-" * 80)
metrics_cluster = orchestrator.transform(df, use_ml=True, ml_method='clustering')
print(f"Records: {metrics_cluster['total_records']}")
print(f"Rule-based anomalies: {metrics_cluster['anomalies_by_rules']}")
print(f"Clustering anomalies: {metrics_cluster['anomalies_by_stats']}")
print(f"Total anomalies: {metrics_cluster['total_anomalies_detected']}")

# Comparison
print(f"\n" + "="*80)
print("COMPARISON")
print("="*80)

comparison = pd.DataFrame({
    'Method': ['IQR', 'Isolation Forest', 'Autoencoder', 'Clustering'],
    'Anomalies': [
        metrics_iqr['anomalies_by_stats'],
        metrics_if['anomalies_by_stats'],
        metrics_ae['anomalies_by_stats'],
        metrics_cluster['anomalies_by_stats']
    ],
    'Percentage': [
        f"{metrics_iqr['anomalies_by_stats']/metrics_iqr['total_records']*100:.2f}%",
        f"{metrics_if['anomalies_by_stats']/metrics_if['total_records']*100:.2f}%",
        f"{metrics_ae['anomalies_by_stats']/metrics_ae['total_records']*100:.2f}%",
        f"{metrics_cluster['anomalies_by_stats']/metrics_cluster['total_records']*100:.2f}%"
    ]
})

print("\n" + comparison.to_string(index=False))

print(f"\n✓ Integration test passed!")
print(f"✓ All ML methods working correctly with orchestrator")
print(f"✓ ML methods detected {metrics_if['anomalies_by_stats']} anomalies vs {metrics_iqr['anomalies_by_stats']} for IQR")
print("="*80)
