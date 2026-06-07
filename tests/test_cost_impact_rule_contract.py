import unittest

from validation.intelligence.cost_impact_rule import (
    CostImpactRule,
)


class TestCostImpactRuleContract(
    unittest.TestCase
):

    def test_rule_has_estimate_method(self):

        self.assertTrue(
            hasattr(
                CostImpactRule,
                "estimate"
            )
        )


if __name__ == "__main__":
    unittest.main()
