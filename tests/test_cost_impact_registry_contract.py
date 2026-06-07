import unittest

from validation.intelligence.cost_impact_registry import (
    CostImpactRegistry,
)


class TestCostImpactRegistryContract(
    unittest.TestCase
):

    def test_registry_has_get_rules(self):

        self.assertTrue(
            hasattr(
                CostImpactRegistry,
                "get_rules"
            )
        )


if __name__ == "__main__":
    unittest.main()
