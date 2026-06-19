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
                "governance_state",
                "legacy_decision_status",
                "dominant_authority",
                "reason_code",
                "warnings",
                "recommendations",
            ],
        )

    def test_build_includes_governance_visibility(self):
        kpi_report, readiness_report, optimization_result = self._inputs()

        report = self.builder.build(
            kpi_report,
            readiness_report,
            optimization_result,
        )

        self.assertEqual(report.governance_state, "APPROVED")
        self.assertEqual(report.legacy_decision_status, "APPROVED")
        self.assertEqual(report.dominant_authority, "FactoryGovernancePolicyBuilder")
        self.assertEqual(report.reason_code, "POLICY_CLEAR")

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

    def test_existing_callers_still_work_without_optional_reports(self):
        kpi_report, readiness_report, optimization_result = self._inputs()

        report = self.builder.build(
            kpi_report,
            readiness_report,
            optimization_result,
        )

        self.assertEqual(report.overall_score, 100)
        self.assertEqual(report.overall_grade, "A")

    def test_overloaded_capacity_reduces_score(self):
        report = self.builder.build(
            *self._inputs(),
            capacity_report=self._capacity_report(
                capacity_status="OVERLOADED",
            ),
        )

        self.assertEqual(report.overall_score, 85)
        self.assertEqual(report.overall_grade, "A")

    def test_high_schedule_risk_reduces_score(self):
        report = self.builder.build(
            *self._inputs(),
            production_schedule_report=self._schedule_report(
                schedule_risk_level="HIGH",
            ),
        )

        self.assertEqual(report.overall_score, 85)
        self.assertEqual(report.overall_grade, "A")

    def test_overloaded_workload_reduces_score(self):
        report = self.builder.build(
            *self._inputs(),
            factory_workload_report=self._workload_report(
                factory_workload_status="OVERLOADED",
            ),
        )

        self.assertEqual(report.overall_score, 85)
        self.assertEqual(report.overall_grade, "A")

    def test_high_complexity_reduces_score(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_complexity_report=self._complexity_report(
                complexity_level="HIGH",
                recommendations=["Review complexity"],
                warnings=["Complexity warning"],
            ),
        )

        self.assertEqual(report.overall_score, 90)
        self.assertEqual(report.overall_grade, "A")

    def test_combined_production_intelligence_penalties_stack(self):
        report = self.builder.build(
            *self._inputs(),
            capacity_report=self._capacity_report(
                capacity_status="LIMITED",
            ),
            production_schedule_report=self._schedule_report(
                schedule_risk_level="MEDIUM",
            ),
            factory_workload_report=self._workload_report(
                factory_workload_status="BUSY",
            ),
            manufacturing_complexity_report=self._complexity_report(
                complexity_level="MEDIUM",
                recommendations=["Review complexity"],
                warnings=["Complexity warning"],
            ),
        )

        self.assertEqual(report.overall_score, 80)
        self.assertEqual(report.overall_grade, "B")

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

    def test_complexity_recommendations_are_appended_without_mutation(self):
        kpi_report, readiness_report, optimization_result = self._inputs()
        complexity_report = self._complexity_report(
            complexity_level="HIGH",
            recommendations=["Review complexity"],
            warnings=["Complexity warning"],
        )

        report = self.builder.build(
            kpi_report,
            readiness_report,
            optimization_result,
            manufacturing_complexity_report=complexity_report,
        )

        self.assertEqual(
            report.recommendations,
            ["Review nesting", "Review complexity"],
        )
        self.assertEqual(
            complexity_report.recommendations,
            ["Review complexity"],
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

    @staticmethod
    def _capacity_report(**values):
        from manufacturing.manufacturing_capacity_report import (
            ManufacturingCapacityReport,
        )

        return ManufacturingCapacityReport(**values)

    @staticmethod
    def _schedule_report(**values):
        from manufacturing.production_schedule_report import (
            ProductionScheduleReport,
        )

        return ProductionScheduleReport(**values)

    @staticmethod
    def _workload_report(**values):
        from manufacturing.factory_workload_report import (
            FactoryWorkloadReport,
        )

        return FactoryWorkloadReport(**values)

    @staticmethod
    def _complexity_report(**values):
        from manufacturing.manufacturing_complexity_report import (
            ManufacturingComplexityReport,
        )

        return ManufacturingComplexityReport(**values)


if __name__ == "__main__":
    unittest.main()
