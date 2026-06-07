import unittest

from validation.intelligence.cost_impact_registry import (
    CostImpactRegistry,
)


class TestCostImpactRegistryExecution(
    unittest.TestCase
):

    def test_registry_returns_rules(self):

        rules = (
            CostImpactRegistry
            .get_rules()
        )

        self.assertGreater(
            len(rules),
            0
        )


if __name__ == "__main__":
    unittest.main()
