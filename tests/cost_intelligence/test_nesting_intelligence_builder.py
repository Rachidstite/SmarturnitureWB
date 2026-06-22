import unittest
from dataclasses import fields, is_dataclass


class TestNestingIntelligenceBuilder(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.nesting_intelligence_builder import (
            NestingIntelligenceBuilder,
        )

        self.builder = NestingIntelligenceBuilder()

    def test_report_is_dataclass_with_required_fields(self):
        from cost_intelligence.nesting_intelligence_report import (
            NestingIntelligenceReport,
        )

        self.assertTrue(is_dataclass(NestingIntelligenceReport))
        self.assertEqual(
            [field.name for field in fields(NestingIntelligenceReport)],
            [
                "utilization_rate",
                "waste_rate",
                "recovery_score",
                "risk_level",
                "recommendation",
                "warnings",
                "reuse_rate",
                "reusable_area",
                "estimated_recovered_value",
            ],
        )

    def test_offcut_values_are_copied_from_waste_report(self):
        report = self.builder.build(
            self._sheet_utilization_report(),
            self._offcut_intelligence_report(
                reuse_rate=0.11,
                reusable_area=2.5,
                estimated_recovered_value=14.0,
            ),
            self._waste_intelligence_report(
                reuse_rate=0.33,
                reusable_area=7.5,
                estimated_recovered_value=28.0,
            ),
        )

        self.assertEqual(report.reuse_rate, 0.33)
        self.assertEqual(report.reusable_area, 7.5)
        self.assertEqual(report.estimated_recovered_value, 28.0)

    def test_falls_back_to_offcut_report_when_waste_report_lacks_fields(self):
        waste_report = self._waste_intelligence_report()
        delattr(waste_report, "reuse_rate")
        delattr(waste_report, "reusable_area")
        delattr(waste_report, "estimated_recovered_value")

        report = self.builder.build(
            self._sheet_utilization_report(),
            self._offcut_intelligence_report(
                reuse_rate=0.19,
                reusable_area=4.5,
                estimated_recovered_value=9.75,
            ),
            waste_report,
        )

        self.assertEqual(report.reuse_rate, 0.19)
        self.assertEqual(report.reusable_area, 4.5)
        self.assertEqual(report.estimated_recovered_value, 9.75)

    def test_missing_offcut_values_keep_safe_defaults(self):
        report = self.builder.build(
            self._sheet_utilization_report(),
            self._offcut_intelligence_report(),
            self._waste_intelligence_report(),
        )

        self.assertEqual(report.reuse_rate, 0.0)
        self.assertEqual(report.reusable_area, 0.0)
        self.assertEqual(report.estimated_recovered_value, 0.0)

    def test_high_waste_risk_has_precedence(self):
        report = self.builder.build(
            self._sheet_utilization_report(utilization_rate=0.80),
            self._offcut_intelligence_report(waste_recovery_score=70),
            self._waste_intelligence_report(risk_level="HIGH"),
        )

        self.assertEqual(report.risk_level, "HIGH")
        self.assertEqual(
            report.recommendation,
            "Improve nesting efficiency and offcut reuse before production",
        )

    def test_low_utilization_is_medium_risk(self):
        report = self.builder.build(
            self._sheet_utilization_report(
                utilization_rate=0.59,
                waste_rate=0.41,
            ),
            self._offcut_intelligence_report(waste_recovery_score=45),
            self._waste_intelligence_report(risk_level="LOW"),
        )

        self.assertEqual(report.utilization_rate, 0.59)
        self.assertEqual(report.waste_rate, 0.41)
        self.assertEqual(report.recovery_score, 45)
        self.assertEqual(report.risk_level, "MEDIUM")
        self.assertEqual(
            report.recommendation,
            "Review nesting layout for better sheet utilization",
        )

    def test_acceptable_utilization_is_low_risk(self):
        report = self.builder.build(
            self._sheet_utilization_report(utilization_rate=0.60),
            self._offcut_intelligence_report(),
            self._waste_intelligence_report(risk_level="MEDIUM"),
        )

        self.assertEqual(report.risk_level, "LOW")
        self.assertEqual(report.recommendation, "Nesting quality acceptable")

    def test_warnings_are_combined_in_order_into_new_list(self):
        sheet_warnings = ["Sheet warning"]
        offcut_warnings = ["Offcut warning"]
        waste_warnings = ["Waste warning"]

        report = self.builder.build(
            self._sheet_utilization_report(warnings=sheet_warnings),
            self._offcut_intelligence_report(warnings=offcut_warnings),
            self._waste_intelligence_report(warnings=waste_warnings),
        )

        self.assertEqual(
            report.warnings,
            [
                "Sheet warning",
                "Offcut warning",
                "Waste warning",
            ],
        )
        self.assertIsNot(report.warnings, sheet_warnings)
        self.assertIsNot(report.warnings, offcut_warnings)
        self.assertIsNot(report.warnings, waste_warnings)

    @staticmethod
    def _sheet_utilization_report(**values):
        from cost_intelligence.sheet_utilization_report import (
            SheetUtilizationReport,
        )

        return SheetUtilizationReport(**values)

    @staticmethod
    def _offcut_intelligence_report(**values):
        from cost_intelligence.offcut_intelligence_report import (
            OffcutIntelligenceReport,
        )

        return OffcutIntelligenceReport(**values)

    @staticmethod
    def _waste_intelligence_report(**values):
        from cost_intelligence.waste_intelligence_report import (
            WasteIntelligenceReport,
        )

        return WasteIntelligenceReport(**values)


if __name__ == "__main__":
    unittest.main()
