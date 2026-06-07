import unittest
from unittest.mock import patch

from validation.intelligence.cost_impact_engine import (
    CostImpactEngine,
)


class TestCostImpactEngineExecution(
    unittest.TestCase
):

    @patch(
        "validation.intelligence.cost_impact_registry.CostImpactRegistry.get_rules"
    )
    def test_engine_executes_rules(
        self,
        get_rules
    ):

        class FakeRule:

            def estimate(
                self,
                panel_specs
            ):
                return ["impact"]

        get_rules.return_value = [
            FakeRule()
        ]

        results = (
            CostImpactEngine()
            .estimate([])
        )

        self.assertEqual(
            len(results),
            1
        )


if __name__ == "__main__":
    unittest.main()
