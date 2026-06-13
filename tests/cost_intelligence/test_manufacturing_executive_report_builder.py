import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingExecutiveReportBuilder(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.manufacturing_executive_report_builder import (
            ManufacturingExecutiveReportBuilder,
        )

        self.builder = ManufacturingExecutiveReportBuilder()

    def test_report_is_dataclass_with_exact_field_order(self):
        from cost_intelligence.manufacturing_executive_report import (
            ManufacturingExecutiveReport,
        )

        self.assertTrue(is_dataclass(ManufacturingExecutiveReport))
        self.assertEqual(
            [field.name for field in fields(ManufacturingExecutiveReport)],
            [
                "overall_score",
                "overall_grade",
                "production_status",
                "total_manufacturing_cost",
                "gross_margin_rate",
                "utilization_rate",
                "waste_rate",
                "recovery_score",
                "warnings",
                "recommendations",
            ],
        )

    def test_build_maps_kpi_fields(self):
        kpi_report, readiness_report, optimization_result = self._inputs()

        report = self.builder.build(
            kpi_report,
            readiness_report,
            optimization_result,
        )

        self.assertEqual(report.production_status, "READY")
        self.assertEqual(report.total_manufacturing_cost, 1250.0)
        self.assertEqual(report.gross_margin_rate, 0.20)
        self.assertEqual(report.utilization_rate, 0.75)
        self.assertEqual(report.waste_rate, 0.25)
        self.assertEqual(report.recovery_score, 60)

    def test_ready_high_performing_project_gets_a(self):
        kpi_report, readiness_report, optimization_result = self._inputs()

        report = self.builder.build(
            kpi_report,
            readiness_report,
            optimization_result,
        )

        self.assertEqual(report.overall_score, 100)
        self.assertEqual(report.overall_grade, "A")

    def test_blocked_risky_project_reduces_score_and_grade(self):
        kpi_report, readiness_report, optimization_result = self._inputs()
        kpi_report.production_status = "BLOCKED"
        kpi_report.gross_margin_rate = 0.0
        kpi_report.utilization_rate = 0.50
        kpi_report.waste_rate = 0.40
        optimization_result.nesting_intelligence_report.recovery_score = 20

        report = self.builder.build(
            kpi_report,
            readiness_report,
            optimization_result,
        )

        self.assertEqual(report.overall_score, 0)
        self.assertEqual(report.overall_grade, "F")

    def test_combines_warnings_into_new_list(self):
        kpi_report, readiness_report, optimization_result = self._inputs()

        report = self.builder.build(
            kpi_report,
            readiness_report,
            optimization_result,
        )

        self.assertEqual(
            report.warnings,
            ["KPI warning", "Readiness warning"],
        )
        self.assertIsNot(report.warnings, kpi_report.warnings)
        self.assertIsNot(report.warnings, readiness_report.warnings)

    def test_carries_recommendations_into_new_list(self):
        kpi_report, readiness_report, optimization_result = self._inputs()

        report = self.builder.build(
            kpi_report,
            readiness_report,
            optimization_result,
        )

        self.assertEqual(report.recommendations, ["Review nesting"])
        self.assertIsNot(
            report.recommendations,
            readiness_report.recommendations,
        )

    def test_builder_does_not_mutate_inputs(self):
        kpi_report, readiness_report, optimization_result = self._inputs()
        original_kpi_warnings = list(kpi_report.warnings)
        original_readiness_warnings = list(readiness_report.warnings)
        original_recommendations = list(readiness_report.recommendations)

        self.builder.build(
            kpi_report,
            readiness_report,
            optimization_result,
        )

        self.assertEqual(kpi_report.warnings, original_kpi_warnings)
        self.assertEqual(readiness_report.warnings, original_readiness_warnings)
        self.assertEqual(
            readiness_report.recommendations,
            original_recommendations,
        )

    @staticmethod
    def _inputs():
        from cost_intelligence.manufacturing_kpi_report import (
            ManufacturingKPIReport,
        )
        from cost_intelligence.manufacturing_optimization_result import (
            ManufacturingOptimizationResult,
        )
        from cost_intelligence.nesting_intelligence_report import (
            NestingIntelligenceReport,
        )
        from cost_intelligence.production_readiness_report import (
            ProductionReadinessReport,
        )

        kpi_report = ManufacturingKPIReport(
            total_manufacturing_cost=1250.0,
            gross_margin_rate=0.20,
            utilization_rate=0.75,
            waste_rate=0.25,
            production_status="READY",
            warnings=["KPI warning"],
        )
        readiness_report = ProductionReadinessReport(
            status="READY",
            warnings=["Readiness warning"],
            recommendations=["Review nesting"],
        )
        optimization_result = ManufacturingOptimizationResult(
            sheet_utilization_report=object(),
            offcut_report=object(),
            offcut_intelligence_report=object(),
            waste_intelligence_report=object(),
            nesting_intelligence_report=NestingIntelligenceReport(
                recovery_score=60,
            ),
        )
        return kpi_report, readiness_report, optimization_result


if __name__ == "__main__":
    unittest.main()
