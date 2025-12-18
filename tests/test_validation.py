# tests/test_validation.py
import unittest
import pandas as pd
from src.validation.rule_validator import RuleValidator

class TestRuleValidator(unittest.TestCase):
    def setUp(self):
        self.validator = RuleValidator(
            required_columns=['id', 'transaction_amount', 'account_balance', 'account_type'],
            allowed_ranges={'transaction_amount': (0, 15000), 'account_balance': (0, 70000)},
            allowed_categories={'account_type': ['Retail', 'Corporate', 'Investment']}
        )

    def test_negative_values_and_nulls(self):
        # Create DataFrame with invalid entries
        df = pd.DataFrame([
            {'id': 1, 'transaction_amount': -50, 'account_balance': 100, 'risk_score': 10, 'account_age': 5, 'account_type': 'Retail'},
            {'id': 2, 'transaction_amount': 20, 'account_balance': None, 'risk_score': 200, 'account_age': -1, 'account_type': 'Unknown'},
            {'id': 3, 'transaction_amount': 0, 'account_balance': 50, 'risk_score': None, 'account_age': 10, 'account_type': 'Corporate'}
        ])
        results = self.validator.validate(df)
        # Expect violations: id=1 (negative amount -> range_violation), id=2 (null balance -> null_or_missing, invalid type -> invalid_category), id=3 (null risk_score but risk_score not required)
        self.assertTrue(results.loc[0, 'range_violation'])  # negative amount
        self.assertTrue(results.loc[1, 'null_or_missing'])  # null balance
        self.assertTrue(results.loc[1, 'invalid_category'])  # invalid account_type
        self.assertTrue(results.loc[0, 'anomaly'])  # overall anomaly
        self.assertTrue(results.loc[1, 'anomaly'])
        self.assertFalse(results.loc[2, 'anomaly'])  # no anomaly for id=3
