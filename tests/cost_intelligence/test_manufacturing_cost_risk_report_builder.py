import unittest


class TestManufacturingCostRiskReportBuilder(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.manufacturing_cost_risk_report_builder import (
            ManufacturingCostRiskReportBuilder,
        )

        self.builder = ManufacturingCostRiskReportBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_low_risk_recommendation(self):
        report = self.builder.build(self._insights(risk_level="LOW"))

        self.assertEqual(report.risk_level, "LOW")
        self.assertEqual(
            report.recommendation,
            "No manufacturing cost risks detected.",
        )

    def test_medium_risk_recommendation(self):
        report = self.builder.build(self._insights(risk_level="MEDIUM"))

        self.assertEqual(report.risk_level, "MEDIUM")
        self.assertEqual(
            report.recommendation,
            "Review manufacturing complexity before quotation.",
        )

    def test_high_risk_maps_findings_and_warnings(self):
        from cost_intelligence.manufacturing_cost_risk_report import (
            ManufacturingCostRiskReport,
        )

        findings = ["High panel count", "High drilling complexity"]
        warnings = ["Invalid panel width"]
        insights = self._insights(
            risk_level="HIGH",
            insights=findings,
            warnings=warnings,
        )

        report = self.builder.build(insights)

        self.assertIsInstance(report, ManufacturingCostRiskReport)
        self.assertEqual(report.risk_level, "HIGH")
        self.assertIs(report.findings, findings)
        self.assertEqual(
            report.recommendation,
            "Review manufacturing complexity before production release.",
        )
        self.assertIs(report.warnings, warnings)

    @staticmethod
    def _insights(**values):
        from cost_intelligence.manufacturing_cost_insights import (
            ManufacturingCostInsights,
        )

        return ManufacturingCostInsights(**values)


if __name__ == "__main__":
    unittest.main()
