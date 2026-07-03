import unittest
from dataclasses import fields, is_dataclass
import inspect


class TestManufacturingKPIBuilder(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.manufacturing_kpi_builder import (
            ManufacturingKPIBuilder,
        )

        self.builder = ManufacturingKPIBuilder()

    def test_report_is_dataclass_with_required_fields(self):
        from cost_intelligence.manufacturing_kpi_report import (
            ManufacturingKPIReport,
        )

        self.assertTrue(is_dataclass(ManufacturingKPIReport))
        self.assertEqual(
            [field.name for field in fields(ManufacturingKPIReport)],
            [
                "total_manufacturing_cost",
                "gross_margin_rate",
                "utilization_rate",
                "waste_rate",
                "reuse_rate",
                "production_status",
                "warnings",
                "project_profitability_status",
                "material_efficiency_status",
                "waste_risk_status",
                "bottleneck_status",
                "production_readiness_status",
                "overall_management_status",
            ],
        )

    def test_build_maps_existing_result_metrics(self):
        cost_summary, optimization_result, commercial_result, readiness_report = (
            self._inputs()
        )

        report = self.builder.build(
            cost_summary,
            optimization_result,
            commercial_result,
            readiness_report,
        )

        self.assertEqual(report.total_manufacturing_cost, 1250.0)
        self.assertEqual(report.gross_margin_rate, 0.20)
        self.assertEqual(report.utilization_rate, 0.75)
        self.assertEqual(report.waste_rate, 0.25)
        self.assertEqual(report.reuse_rate, 0.60)
        self.assertEqual(report.production_status, "READY_WITH_WARNINGS")
        self.assertEqual(report.project_profitability_status, "HEALTHY")
        self.assertEqual(report.material_efficiency_status, "EFFICIENT")
        self.assertEqual(report.waste_risk_status, "MEDIUM")
        self.assertEqual(report.bottleneck_status, "UNKNOWN")
        self.assertEqual(
            report.production_readiness_status,
            "READY_WITH_WARNINGS",
        )
        self.assertEqual(report.overall_management_status, "MONITOR")

    def test_warnings_are_combined_in_order_into_new_list(self):
        cost_summary, optimization_result, commercial_result, readiness_report = (
            self._inputs()
        )
        source_warning_lists = [
            cost_summary.warnings,
            optimization_result.sheet_utilization_report.warnings,
            optimization_result.offcut_intelligence_report.warnings,
            optimization_result.waste_intelligence_report.warnings,
            optimization_result.nesting_intelligence_report.warnings,
            readiness_report.warnings,
        ]

        report = self.builder.build(
            cost_summary,
            optimization_result,
            commercial_result,
            readiness_report,
        )

        self.assertEqual(
            report.warnings,
            [
                "Cost warning",
                "Sheet warning",
                "Offcut warning",
                "Waste warning",
                "Nesting warning",
                "Readiness warning",
            ],
        )
        for source_warnings in source_warning_lists:
            self.assertIsNot(report.warnings, source_warnings)

    def test_builder_does_not_mutate_inputs(self):
        cost_summary, optimization_result, commercial_result, readiness_report = (
            self._inputs()
        )
        original_cost_warnings = list(cost_summary.warnings)
        original_readiness_warnings = list(readiness_report.warnings)

        self.builder.build(
            cost_summary,
            optimization_result,
            commercial_result,
            readiness_report,
        )

        self.assertEqual(cost_summary.warnings, original_cost_warnings)
        self.assertEqual(readiness_report.warnings, original_readiness_warnings)

    def test_management_status_fields_are_deterministic(self):
        cost_summary, optimization_result, commercial_result, readiness_report = (
            self._inputs()
        )
        readiness_report.status = "BLOCKED"
        commercial_result.profitability_report.gross_margin_rate = 0.0
        optimization_result.sheet_utilization_report.waste_rate = 0.35

        report = self.builder.build(
            cost_summary,
            optimization_result,
            commercial_result,
            readiness_report,
        )

        self.assertEqual(report.project_profitability_status, "CRITICAL")
        self.assertEqual(report.material_efficiency_status, "EFFICIENT")
        self.assertEqual(report.waste_risk_status, "HIGH")
        self.assertEqual(report.production_readiness_status, "BLOCKED")
        self.assertEqual(report.overall_management_status, "ACTION_REQUIRED")

    def test_optional_bottleneck_report_is_mapped_without_new_import_dependency(self):
        cost_summary, optimization_result, commercial_result, readiness_report = (
            self._inputs()
        )
        from manufacturing.factory_bottleneck_intelligence_report import (
            FactoryBottleneckIntelligenceReport,
        )

        report = self.builder.build(
            cost_summary,
            optimization_result,
            commercial_result,
            readiness_report,
            factory_bottleneck_intelligence_report=(
                FactoryBottleneckIntelligenceReport(severity="HIGH")
            ),
        )

        self.assertEqual(report.bottleneck_status, "HIGH")
        self.assertEqual(report.overall_management_status, "ACTION_REQUIRED")

        from cost_intelligence.manufacturing_kpi_builder import (
            ManufacturingKPIBuilder,
        )

        source = inspect.getsource(ManufacturingKPIBuilder)
        self.assertNotIn("from manufacturing", source)
        self.assertNotIn("import manufacturing", source)

    @staticmethod
    def _inputs():
        from cost_intelligence.manufacturing_commercial_result import (
            ManufacturingCommercialResult,
        )
        from cost_intelligence.manufacturing_cost_summary import (
            ManufacturingCostSummary,
        )
        from cost_intelligence.manufacturing_optimization_result import (
            ManufacturingOptimizationResult,
        )
        from cost_intelligence.nesting_intelligence_report import (
            NestingIntelligenceReport,
        )
        from cost_intelligence.offcut_intelligence_report import (
            OffcutIntelligenceReport,
        )
        from cost_intelligence.offcut_report import OffcutReport
        from cost_intelligence.production_readiness_report import (
            ProductionReadinessReport,
        )
        from cost_intelligence.profitability_report import ProfitabilityReport
        from cost_intelligence.sheet_utilization_report import (
            SheetUtilizationReport,
        )
        from cost_intelligence.waste_intelligence_report import (
            WasteIntelligenceReport,
        )

        cost_summary = ManufacturingCostSummary(
            total_manufacturing_cost=1250.0,
            warnings=["Cost warning"],
        )
        optimization_result = ManufacturingOptimizationResult(
            sheet_utilization_report=SheetUtilizationReport(
                utilization_rate=0.75,
                waste_rate=0.25,
                warnings=["Sheet warning"],
            ),
            offcut_report=OffcutReport(),
            offcut_intelligence_report=OffcutIntelligenceReport(
                reuse_rate=0.60,
                warnings=["Offcut warning"],
            ),
            waste_intelligence_report=WasteIntelligenceReport(
                warnings=["Waste warning"],
            ),
            nesting_intelligence_report=NestingIntelligenceReport(
                warnings=["Nesting warning"],
            ),
        )
        commercial_result = ManufacturingCommercialResult(
            manufacturing_cost_summary=cost_summary,
            manufacturing_quotation_input=object(),
            quotation_report=object(),
            profitability_report=ProfitabilityReport(gross_margin_rate=0.20),
        )
        readiness_report = ProductionReadinessReport(
            status="READY_WITH_WARNINGS",
            warnings=["Readiness warning"],
        )
        return cost_summary, optimization_result, commercial_result, readiness_report


if __name__ == "__main__":
    unittest.main()
