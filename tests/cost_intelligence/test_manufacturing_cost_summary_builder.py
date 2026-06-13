import unittest


class TestManufacturingCostSummaryBuilder(unittest.TestCase):

    def test_manufacturing_cost_summary_builder_exists(self):
        from cost_intelligence.manufacturing_cost_summary_builder import (
            ManufacturingCostSummaryBuilder,
        )

        self.assertTrue(callable(ManufacturingCostSummaryBuilder().build))

    def test_build_returns_manufacturing_cost_summary(self):
        from cost_intelligence.manufacturing_cost_insights import (
            ManufacturingCostInsights,
        )
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )
        from cost_intelligence.manufacturing_cost_risk_report import (
            ManufacturingCostRiskReport,
        )
        from cost_intelligence.manufacturing_cost_summary import (
            ManufacturingCostSummary,
        )
        from cost_intelligence.manufacturing_cost_summary_builder import (
            ManufacturingCostSummaryBuilder,
        )

        cost_report = ManufacturingCostReport(total_manufacturing_cost=123.0)
        risk_report = ManufacturingCostRiskReport(
            risk_level="HIGH",
            warnings=["manufacturing warning"],
        )
        insights = ManufacturingCostInsights(insights=["High panel count"])

        summary = ManufacturingCostSummaryBuilder().build(
            cost_report, risk_report, insights
        )

        self.assertIsInstance(summary, ManufacturingCostSummary)
        self.assertIs(summary.cost_report, cost_report)
        self.assertIs(summary.risk_report, risk_report)
        self.assertIs(summary.insights, insights)
        self.assertEqual(summary.total_manufacturing_cost, 123.0)
        self.assertEqual(summary.risk_level, "HIGH")
        self.assertEqual(summary.warnings, ["manufacturing warning"])


if __name__ == "__main__":
    unittest.main()
