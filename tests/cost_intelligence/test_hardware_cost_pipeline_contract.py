import inspect
import unittest
from dataclasses import fields
from types import SimpleNamespace
from unittest.mock import patch


class TestHardwareCostPipelineContract(unittest.TestCase):

    def _zero_metrics_context(self):
        return SimpleNamespace(
            total_panels=0,
            total_panel_area_m2=0.0,
            total_edge_meters=0.0,
            edge_meters_by_banding={},
            total_drilling_operations=0,
            machining_operations_by_type={},
            total_material_types=0,
            warnings=[],
        )

    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingCostSummaryBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingCostCalculator"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingCostRiskReportBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingCostInsightsBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingCostContextBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingDurationBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "LaborCostBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingMetricsBuilder"
    )
    def test_manufacturing_cost_pipeline_accepts_hardware_cost_input(
        self,
        metrics_builder_class,
        labor_cost_builder_class,
        duration_builder_class,
        context_builder_class,
        insights_builder_class,
        risk_report_builder_class,
        cost_calculator_class,
        summary_builder_class,
    ):
        from cost_intelligence.manufacturing_cost_pipeline_builder import (
            ManufacturingCostPipelineBuilder,
        )

        production_package = object()
        metrics_report = object()
        context = self._zero_metrics_context()
        duration_report = object()
        labor_cost_report = object()
        insights = object()
        risk_report = object()
        cost_report = object()
        summary = object()

        metrics_builder_class.return_value.build.return_value = metrics_report
        duration_builder_class.return_value.build.return_value = duration_report
        labor_cost_builder_class.return_value.build.return_value = labor_cost_report
        context_builder_class.return_value.build.return_value = context
        insights_builder_class.return_value.build.return_value = insights
        risk_report_builder_class.return_value.build.return_value = risk_report
        cost_calculator_class.return_value.calculate.return_value = cost_report
        summary_builder_class.return_value.build.return_value = summary

        result = ManufacturingCostPipelineBuilder().build(
            production_package,
            hardware_cost=48.0,
        )

        self.assertIs(result, summary)
        metrics_builder_class.return_value.build.assert_called_once_with(
            production_package
        )
        duration_builder_class.return_value.build.assert_called_once_with(
            metrics_report
        )
        labor_cost_builder_class.return_value.build.assert_called_once_with(
            duration_report
        )
        context_builder_class.return_value.build.assert_called_once_with(
            metrics_report
        )
        insights_builder_class.return_value.build.assert_called_once_with(context)
        risk_report_builder_class.return_value.build.assert_called_once_with(
            insights
        )
        cost_calculator_class.return_value.calculate.assert_called_once_with(
            context,
            hardware_cost=48.0,
            labor_cost_report=labor_cost_report,
            sheet_cost=None,
            waste_cost=None,
            recovered_value=None,
        )
        summary_builder_class.return_value.build.assert_called_once_with(
            cost_report,
            risk_report,
            insights,
        )

    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingCostSummaryBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingCostCalculator"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingCostRiskReportBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingCostInsightsBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingCostContextBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingDurationBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "LaborCostBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_cost_pipeline_builder."
        "ManufacturingMetricsBuilder"
    )
    def test_manufacturing_cost_pipeline_preserves_existing_total_when_hardware_cost_absent(
        self,
        metrics_builder_class,
        labor_cost_builder_class,
        duration_builder_class,
        context_builder_class,
        insights_builder_class,
        risk_report_builder_class,
        cost_calculator_class,
        summary_builder_class,
    ):
        from cost_intelligence.manufacturing_cost_pipeline_builder import (
            ManufacturingCostPipelineBuilder,
        )

        production_package = object()
        metrics_report = object()
        context = self._zero_metrics_context()
        duration_report = object()
        labor_cost_report = object()
        insights = object()
        risk_report = object()
        cost_report = SimpleNamespace(total_manufacturing_cost=123.45)
        summary = SimpleNamespace(
            cost_report=cost_report,
            risk_report=risk_report,
            insights=insights,
            total_manufacturing_cost=123.45,
            risk_level="LOW",
            warnings=[],
        )

        metrics_builder_class.return_value.build.return_value = metrics_report
        duration_builder_class.return_value.build.return_value = duration_report
        labor_cost_builder_class.return_value.build.return_value = labor_cost_report
        context_builder_class.return_value.build.return_value = context
        insights_builder_class.return_value.build.return_value = insights
        risk_report_builder_class.return_value.build.return_value = risk_report
        cost_calculator_class.return_value.calculate.return_value = cost_report
        summary_builder_class.return_value.build.return_value = summary

        result = ManufacturingCostPipelineBuilder().build(production_package)

        self.assertIs(result, summary)
        self.assertEqual(result.total_manufacturing_cost, 123.45)
        metrics_builder_class.return_value.build.assert_called_once_with(
            production_package
        )
        duration_builder_class.return_value.build.assert_called_once_with(
            metrics_report
        )
        labor_cost_builder_class.return_value.build.assert_called_once_with(
            duration_report
        )
        context_builder_class.return_value.build.assert_called_once_with(
            metrics_report
        )
        insights_builder_class.return_value.build.assert_called_once_with(context)
        risk_report_builder_class.return_value.build.assert_called_once_with(
            insights
        )
        cost_calculator_class.return_value.calculate.assert_called_once_with(
            context,
            hardware_cost=0.0,
            labor_cost_report=labor_cost_report,
            sheet_cost=None,
            waste_cost=None,
            recovered_value=None,
        )
        summary_builder_class.return_value.build.assert_called_once_with(
            cost_report,
            risk_report,
            insights,
        )

    def test_manufacturing_cost_report_exposes_hardware_cost_field(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        self.assertIn(
            "hardware_cost",
            [field.name for field in fields(ManufacturingCostReport)],
        )

    def test_manufacturing_cost_summary_exposes_hardware_cost_field(self):
        from cost_intelligence.manufacturing_cost_summary import (
            ManufacturingCostSummary,
        )

        self.assertIn(
            "hardware_cost",
            [field.name for field in fields(ManufacturingCostSummary)],
        )

    def test_hardware_cost_contributes_to_total_manufacturing_cost(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )

        context = self._zero_metrics_context()

        report = ManufacturingCostCalculator().calculate(
            context,
            hardware_cost=48.0,
        )

        self.assertEqual(report.hardware_cost, 48.0)
        self.assertEqual(report.total_manufacturing_cost, 48.0)

    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "QuotationIntelligenceBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "ManufacturingCostPipelineBuilder"
    )
    def test_manufacturing_commercial_pipeline_uses_augmented_total_for_quotation_base_cost(
        self,
        cost_builder_class,
        quotation_intelligence_builder_class,
    ):
        from cost_intelligence.manufacturing_commercial_pipeline_builder import (
            ManufacturingCommercialPipelineBuilder,
        )

        production_package = object()
        augmented_summary = SimpleNamespace(
            total_manufacturing_cost=648.0,
            warnings=[],
            risk_level="LOW",
        )
        quotation_intelligence_report = object()

        cost_builder_class.return_value.build.return_value = augmented_summary
        quotation_intelligence_builder_class.return_value.build.return_value = (
            quotation_intelligence_report
        )

        result = ManufacturingCommercialPipelineBuilder().build(
            production_package,
            markup_rate=0.25,
            currency="EUR",
        )

        self.assertEqual(
            result.manufacturing_quotation_input.base_cost,
            648.0,
        )
        self.assertEqual(
            result.quotation_report.production_cost,
            648.0,
        )
        cost_builder_class.return_value.build.assert_called_once_with(
            production_package
        )
        quotation_intelligence_builder_class.return_value.build.assert_called_once()

    @patch(
        "cost_intelligence.hardware_report_cost_service.HardwareCostCalculator"
    )
    @patch(
        "cost_intelligence.hardware_report_cost_service.HardwareReportItemsAdapter"
    )
    @patch("cost_intelligence.hardware_report_cost_service.HardwareReportEngine")
    def test_hardware_report_cost_service_remains_single_source_of_truth(
        self,
        hardware_report_engine,
        hardware_report_items_adapter,
        hardware_cost_calculator_class,
    ):
        from cost_intelligence.hardware_report_cost_service import (
            HardwareReportCostService,
        )

        project = SimpleNamespace(
            placements=[
                SimpleNamespace(hardware_intent="INTENT_HINGE"),
                SimpleNamespace(hardware_intent="INTENT_MINIFIX_15"),
            ]
        )
        context = SimpleNamespace(
            hardware_profile={
                "INTENT_HINGE": "HINGE_BLUM_110_V1",
                "INTENT_MINIFIX_15": "MINIFIX_15_V1",
            }
        )
        pricing_catalog = {
            "HINGE_BLUM_110_V1": {"unit_price": 6.0},
            "MINIFIX_15_V1": {"unit_price": 1.5},
        }
        hardware_report = SimpleNamespace(hardware_items={"HINGE": 1})
        adapted_items = [{"sku": "HINGE_BLUM_110_V1", "quantity": 1}]
        cost_estimate = SimpleNamespace(hardware_cost=6.0, total_cost=6.0)

        hardware_report_engine.generate_from_project.return_value = (
            hardware_report
        )
        hardware_report_items_adapter.from_report.return_value = adapted_items
        hardware_cost_calculator_class.return_value.estimate.return_value = (
            cost_estimate
        )

        result = HardwareReportCostService.estimate_from_project(
            project,
            context,
            pricing_catalog=pricing_catalog,
        )

        hardware_report_engine.generate_from_project.assert_called_once_with(
            project,
            context,
        )
        hardware_report_items_adapter.from_report.assert_called_once_with(
            hardware_report
        )
        hardware_cost_calculator_class.return_value.estimate.assert_called_once_with(
            hardware_items=adapted_items,
            pricing_catalog=pricing_catalog,
        )
        self.assertIs(result, cost_estimate)

    def test_legacy_project_cost_calculator_is_not_modified(self):
        from cost_intelligence.project_cost_calculator import (
            ProjectCostCalculator,
        )

        signature = inspect.signature(ProjectCostCalculator.estimate)

        self.assertIn("hardware_items", signature.parameters)
        self.assertIn("scene_graph", signature.parameters)
        self.assertIn("project", signature.parameters)
        self.assertNotIn("hardware_cost", signature.parameters)


if __name__ == "__main__":
    unittest.main()
