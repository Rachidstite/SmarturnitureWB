import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingCostSummaryContract(unittest.TestCase):

    def test_manufacturing_cost_summary_is_dataclass(self):
        from cost_intelligence.manufacturing_cost_summary import (
            ManufacturingCostSummary,
        )

        self.assertTrue(is_dataclass(ManufacturingCostSummary))

    def test_manufacturing_cost_summary_fields(self):
        from cost_intelligence.manufacturing_cost_summary import (
            ManufacturingCostSummary,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingCostSummary)],
            [
                "cost_report",
                "risk_report",
                "insights",
                "total_manufacturing_cost",
                "risk_level",
                "warnings",
            ],
        )

    def test_manufacturing_cost_summary_defaults(self):
        from cost_intelligence.manufacturing_cost_summary import (
            ManufacturingCostSummary,
        )

        summary = ManufacturingCostSummary()

        self.assertIsNone(summary.cost_report)
        self.assertIsNone(summary.risk_report)
        self.assertIsNone(summary.insights)
        self.assertEqual(summary.total_manufacturing_cost, 0.0)
        self.assertEqual(summary.risk_level, "LOW")
        self.assertEqual(summary.warnings, [])


if __name__ == "__main__":
    unittest.main()
