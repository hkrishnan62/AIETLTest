# tests/test_validation.py
import unittest
import pandas as pd
from src.validation.rule_validator import RuleValidator

class TestRuleValidator(unittest.TestCase):
    def setUp(self):
        self.validator = RuleValidator()

    def test_negative_values_and_nulls(self):
        # Create DataFrame with invalid entries
        df = pd.DataFrame([
            {'id': 1, 'transaction_amount': -50, 'account_balance': 100, 'risk_score': 10, 'account_age': 5, 'account_type': 'Retail'},
            {'id': 2, 'transaction_amount': 20, 'account_balance': None, 'risk_score': 200, 'account_age': -1, 'account_type': 'Unknown'},
            {'id': 3, 'transaction_amount': 0, 'account_balance': 50, 'risk_score': None, 'account_age': 10, 'account_type': 'Corporate'}
        ])
        issues = self.validator.check(df, stage="extract")
        # Expect violations for id=1 (negative amount), id=2 (null balance, risk_score >100, negative age, invalid type), id=3 (null risk_score)
        self.assertTrue(any("transaction_amount negative" in msg and "1" in msg for msg in issues))
        self.assertTrue(any("account_balance is null" in msg and "2" in msg for msg in issues))
        self.assertTrue(any("risk_score above 100" in msg and "2" in msg for msg in issues))
        self.assertTrue(any("account_age negative" in msg and "2" in msg for msg in issues))
        self.assertTrue(any("invalid account_type" in msg and "2" in msg for msg in issues))
        self.assertTrue(any("risk_score is null" in msg and "3" in msg for msg in issues))
