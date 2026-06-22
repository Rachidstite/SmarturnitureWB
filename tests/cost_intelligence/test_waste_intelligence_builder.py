import unittest
from dataclasses import fields, is_dataclass


class TestWasteIntelligenceBuilder(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.waste_intelligence_builder import (
            WasteIntelligenceBuilder,
        )

        self.builder = WasteIntelligenceBuilder()

    def test_report_is_dataclass_with_required_fields(self):
        from cost_intelligence.waste_intelligence_report import (
            WasteIntelligenceReport,
        )

        self.assertTrue(is_dataclass(WasteIntelligenceReport))
        self.assertEqual(
            [field.name for field in fields(WasteIntelligenceReport)],
            [
                "waste_ratio",
                "waste_cost",
                "recovery_score",
                "risk_level",
                "recommendation",
                "warnings",
                "reuse_rate",
                "reusable_area",
                "largest_reusable_area",
                "estimated_recovered_value",
            ],
        )

    def test_offcut_values_are_copied_into_waste_report(self):
        report = self.builder.build(
            self._consumption_report(),
            self._cost_estimate(),
            self._offcut_intelligence_report(
                reuse_rate=0.42,
                reusable_area=3.5,
                largest_reusable_area=2.25,
                estimated_recovered_value=18.75,
            ),
        )

        self.assertEqual(report.reuse_rate, 0.42)
        self.assertEqual(report.reusable_area, 3.5)
        self.assertEqual(report.largest_reusable_area, 2.25)
        self.assertEqual(report.estimated_recovered_value, 18.75)

    def test_missing_offcut_report_keeps_safe_defaults(self):
        report = self.builder.build(
            self._consumption_report(),
            self._cost_estimate(),
        )

        self.assertEqual(report.reuse_rate, 0.0)
        self.assertEqual(report.reusable_area, 0.0)
        self.assertEqual(report.largest_reusable_area, 0.0)
        self.assertEqual(report.estimated_recovered_value, 0.0)

    def test_high_waste_and_low_recovery_is_high_risk(self):
        report = self.builder.build(
            self._consumption_report(waste_ratio=0.30),
            self._cost_estimate(waste_cost=125.0),
            self._offcut_intelligence_report(waste_recovery_score=39),
        )

        self.assertEqual(report.waste_ratio, 0.30)
        self.assertEqual(report.waste_cost, 125.0)
        self.assertEqual(report.recovery_score, 39)
        self.assertEqual(report.risk_level, "HIGH")
        self.assertEqual(
            report.recommendation,
            "High waste risk: improve nesting or reuse policy",
        )

    def test_high_waste_with_recovery_is_medium_risk(self):
        report = self.builder.build(
            self._consumption_report(waste_ratio=0.30),
            self._cost_estimate(),
            self._offcut_intelligence_report(waste_recovery_score=40),
        )

        self.assertEqual(report.risk_level, "MEDIUM")
        self.assertEqual(
            report.recommendation,
            "Moderate waste risk: review sheet utilization",
        )

    def test_moderate_waste_is_medium_risk(self):
        report = self.builder.build(
            self._consumption_report(waste_ratio=0.15),
            self._cost_estimate(),
        )

        self.assertEqual(report.recovery_score, 0)
        self.assertEqual(report.risk_level, "MEDIUM")

    def test_low_waste_is_low_risk(self):
        report = self.builder.build(
            self._consumption_report(waste_ratio=0.14),
            self._cost_estimate(),
        )

        self.assertEqual(report.risk_level, "LOW")
        self.assertEqual(report.recommendation, "Waste level acceptable")

    def test_warnings_are_combined_in_order_into_new_list(self):
        consumption_warnings = ["Consumption warning"]
        cost_warnings = ["Cost warning"]
        offcut_warnings = ["Offcut warning"]

        report = self.builder.build(
            self._consumption_report(warnings=consumption_warnings),
            self._cost_estimate(warnings=cost_warnings),
            self._offcut_intelligence_report(warnings=offcut_warnings),
        )

        self.assertEqual(
            report.warnings,
            [
                "Consumption warning",
                "Cost warning",
                "Offcut warning",
            ],
        )
        self.assertIsNot(report.warnings, consumption_warnings)
        self.assertIsNot(report.warnings, cost_warnings)
        self.assertIsNot(report.warnings, offcut_warnings)

    @staticmethod
    def _consumption_report(**values):
        from cost_intelligence.consumption_report import ConsumptionReport

        return ConsumptionReport(**values)

    @staticmethod
    def _cost_estimate(**values):
        from cost_intelligence.cost_estimate import CostEstimate

        return CostEstimate(**values)

    @staticmethod
    def _offcut_intelligence_report(**values):
        from cost_intelligence.offcut_intelligence_report import (
            OffcutIntelligenceReport,
        )

        return OffcutIntelligenceReport(**values)


if __name__ == "__main__":
    unittest.main()
