import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingCostInsightsContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from cost_intelligence.manufacturing_cost_insights import (
            ManufacturingCostInsights,
        )

        self.assertTrue(is_dataclass(ManufacturingCostInsights))

    def test_contract_has_required_fields(self):
        from cost_intelligence.manufacturing_cost_insights import (
            ManufacturingCostInsights,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingCostInsights)],
            ["insights", "risk_level", "warnings"],
        )

    def test_contract_defaults(self):
        from cost_intelligence.manufacturing_cost_insights import (
            ManufacturingCostInsights,
        )

        insights = ManufacturingCostInsights()

        self.assertEqual(insights.insights, [])
        self.assertEqual(insights.risk_level, "LOW")
        self.assertEqual(insights.warnings, [])

    def test_list_defaults_are_independent(self):
        from cost_intelligence.manufacturing_cost_insights import (
            ManufacturingCostInsights,
        )

        first_insights = ManufacturingCostInsights()
        second_insights = ManufacturingCostInsights()

        self.assertIsNot(first_insights.insights, second_insights.insights)
        self.assertIsNot(first_insights.warnings, second_insights.warnings)


if __name__ == "__main__":
    unittest.main()
