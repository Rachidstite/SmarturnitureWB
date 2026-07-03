import unittest


class TestFurnitureProjectExecutiveReportBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.furniture_project_executive_report_builder import (
            FurnitureProjectExecutiveReportBuilder,
        )

        self.assertTrue(callable(FurnitureProjectExecutiveReportBuilder().build))

    def test_builder_returns_furniture_project_executive_report(self):
        from cost_intelligence.furniture_project_executive_report import (
            FurnitureProjectExecutiveReport,
        )
        from cost_intelligence.furniture_project_executive_report_builder import (
            FurnitureProjectExecutiveReportBuilder,
        )

        report = FurnitureProjectExecutiveReportBuilder().build(
            self._project_summary(),
            self._manufacturing_executive_report(),
            self._factory_decision_report(),
        )

        self.assertIsInstance(report, FurnitureProjectExecutiveReport)

    def test_builder_maps_summary_executive_and_decision_fields(self):
        from cost_intelligence.furniture_project_executive_report_builder import (
            FurnitureProjectExecutiveReportBuilder,
        )

        report = FurnitureProjectExecutiveReportBuilder().build(
            self._project_summary(
                total_cabinets=3,
                total_physical_parts=42,
                total_machining_operations=96,
            ),
            self._manufacturing_executive_report(
                overall_score=87,
                overall_grade="A",
                production_status="READY",
                total_manufacturing_cost=12500.0,
                gross_margin_rate=0.28,
                utilization_rate=0.78,
                waste_rate=0.22,
                recovery_score=66,
                warnings=["Executive warning"],
                recommendations=["Executive recommendation"],
            ),
            self._factory_decision_report(
                decision_status="APPROVED",
                warnings=["Decision warning"],
                recommendations=["Decision recommendation"],
            ),
        )

        self.assertEqual(report.total_cabinets, 3)
        self.assertEqual(report.total_physical_parts, 42)
        self.assertEqual(report.total_machining_operations, 96)
        self.assertEqual(report.overall_score, 87)
        self.assertEqual(report.overall_grade, "A")
        self.assertEqual(report.decision_status, "APPROVED")
        self.assertEqual(report.production_status, "READY")
        self.assertEqual(report.total_manufacturing_cost, 12500.0)
        self.assertEqual(report.gross_margin_rate, 0.28)
        self.assertEqual(report.utilization_rate, 0.78)
        self.assertEqual(report.waste_rate, 0.22)
        self.assertEqual(report.recovery_score, 66)
        self.assertEqual(report.project_profitability_status, "HEALTHY")
        self.assertEqual(report.material_efficiency_status, "EFFICIENT")
        self.assertEqual(report.waste_risk_status, "MEDIUM")
        self.assertEqual(report.bottleneck_status, "LOW")
        self.assertEqual(report.production_readiness_status, "READY")
        self.assertEqual(report.overall_management_status, "HEALTHY")
        self.assertEqual(
            report.warnings,
            ["Executive warning", "Decision warning"],
        )
        self.assertEqual(
            report.recommendations,
            ["Executive recommendation", "Decision recommendation"],
        )

    def test_builder_does_not_mutate_inputs(self):
        from cost_intelligence.furniture_project_executive_report_builder import (
            FurnitureProjectExecutiveReportBuilder,
        )

        project_summary = self._project_summary()
        executive_report = self._manufacturing_executive_report(
            warnings=["Executive warning"],
            recommendations=["Executive recommendation"],
        )
        decision_report = self._factory_decision_report(
            warnings=["Decision warning"],
            recommendations=["Decision recommendation"],
        )

        original_summary = project_summary.__dict__.copy()
        original_executive = executive_report.__dict__.copy()
        original_decision = decision_report.__dict__.copy()

        FurnitureProjectExecutiveReportBuilder().build(
            project_summary,
            executive_report,
            decision_report,
        )

        self.assertEqual(project_summary.__dict__, original_summary)
        self.assertEqual(executive_report.__dict__, original_executive)
        self.assertEqual(decision_report.__dict__, original_decision)

    def test_builder_reuses_management_status_fields_from_executive_report(self):
        from cost_intelligence.furniture_project_executive_report_builder import (
            FurnitureProjectExecutiveReportBuilder,
        )

        executive_report = self._manufacturing_executive_report(
            project_profitability_status="LOW",
            material_efficiency_status="STABLE",
            waste_risk_status="HIGH",
            bottleneck_status="MEDIUM",
            production_readiness_status="READY_WITH_WARNINGS",
            overall_management_status="MONITOR",
        )

        report = FurnitureProjectExecutiveReportBuilder().build(
            self._project_summary(),
            executive_report,
            self._factory_decision_report(),
        )

        self.assertEqual(report.project_profitability_status, "LOW")
        self.assertEqual(report.material_efficiency_status, "STABLE")
        self.assertEqual(report.waste_risk_status, "HIGH")
        self.assertEqual(report.bottleneck_status, "MEDIUM")
        self.assertEqual(report.production_readiness_status, "READY_WITH_WARNINGS")
        self.assertEqual(report.overall_management_status, "MONITOR")

    @staticmethod
    def _project_summary(
        total_cabinets=0,
        total_physical_parts=0,
        total_machining_operations=0,
    ):
        from manufacturing.furniture_project_summary import FurnitureProjectSummary

        return FurnitureProjectSummary(
            total_cabinets=total_cabinets,
            total_physical_parts=total_physical_parts,
            total_machining_operations=total_machining_operations,
        )

    @staticmethod
    def _manufacturing_executive_report(
        overall_score=0,
        overall_grade="F",
        production_status="",
        total_manufacturing_cost=0.0,
        gross_margin_rate=0.0,
        utilization_rate=0.0,
        waste_rate=0.0,
        recovery_score=0,
        warnings=None,
        recommendations=None,
        project_profitability_status="HEALTHY",
        material_efficiency_status="EFFICIENT",
        waste_risk_status="MEDIUM",
        bottleneck_status="LOW",
        production_readiness_status="READY",
        overall_management_status="HEALTHY",
    ):
        from cost_intelligence.manufacturing_executive_report import (
            ManufacturingExecutiveReport,
        )

        return ManufacturingExecutiveReport(
            overall_score=overall_score,
            overall_grade=overall_grade,
            production_status=production_status,
            total_manufacturing_cost=total_manufacturing_cost,
            gross_margin_rate=gross_margin_rate,
            utilization_rate=utilization_rate,
            waste_rate=waste_rate,
            recovery_score=recovery_score,
            warnings=[] if warnings is None else warnings,
            recommendations=[] if recommendations is None else recommendations,
            project_profitability_status=project_profitability_status,
            material_efficiency_status=material_efficiency_status,
            waste_risk_status=waste_risk_status,
            bottleneck_status=bottleneck_status,
            production_readiness_status=production_readiness_status,
            overall_management_status=overall_management_status,
        )

    @staticmethod
    def _factory_decision_report(
        decision_status="BLOCKED",
        warnings=None,
        recommendations=None,
    ):
        from cost_intelligence.factory_decision_report import FactoryDecisionReport

        return FactoryDecisionReport(
            decision_status=decision_status,
            warnings=[] if warnings is None else warnings,
            recommendations=[] if recommendations is None else recommendations,
        )


if __name__ == "__main__":
    unittest.main()
