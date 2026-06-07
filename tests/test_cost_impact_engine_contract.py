import unittest

from validation.intelligence.cost_impact_engine import (
    CostImpactEngine,
)


class TestCostImpactEngineContract(
    unittest.TestCase
):

    def test_engine_has_estimate_method(self):

        self.assertTrue(
            hasattr(
                CostImpactEngine,
                "estimate"
            )
        )


if __name__ == "__main__":
    unittest.main()
