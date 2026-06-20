import unittest
from unittest.mock import MagicMock, call, patch


class TestFurnitureProjectBusinessReportBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.furniture_project_business_report_builder import (
            FurnitureProjectBusinessReportBuilder,
        )

        self.assertTrue(callable(FurnitureProjectBusinessReportBuilder().build))

    @patch(
        "cost_intelligence.furniture_project_business_report_builder."
        "ManufacturingMetricsBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_business_report_builder."
        "ManufacturingCapacityBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_business_report_builder."
        "ManufacturingDurationBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_business_report_builder."
        "ManufacturingComplexityBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_business_report_builder."
        "ManufacturingProductionPackageBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_business_report_builder."
        "FurnitureProjectManufacturingPackageBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_business_report_builder."
        "FurnitureProjectFactoryDecisionBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_business_report_builder."
        "FurnitureProjectProfitabilityBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_business_report_builder."
        "FurnitureProjectQuotationBreakdownBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_business_report_builder."
        "FurnitureProjectQuotationBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_business_report_builder."
        "FurnitureProjectSummaryBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_business_report_builder."
        "JoineryIntelligenceBuilder"
    )
    def test_builder_aggregates_existing_project_outputs(
        self,
        joinery_builder_class,
        summary_builder_class,
        quotation_builder_class,
        breakdown_builder_class,
        profitability_builder_class,
        decision_builder_class,
        project_package_builder_class,
        production_package_builder_class,
        complexity_builder_class,
        duration_builder_class,
        capacity_builder_class,
        metrics_builder_class,
    ):
        from cost_intelligence.furniture_project_business_report import (
            FurnitureProjectBusinessReport,
        )
        from cost_intelligence.furniture_project_business_report_builder import (
            FurnitureProjectBusinessReportBuilder,
        )

        furniture_project = object()
        project_summary = object()
        quotation_document = object()
        quotation_breakdowns = [{"cabinet_index": 1}]
        manufacturing_complexity_report = object()
        manufacturing_duration_report = object()
        manufacturing_capacity_report = object()
        profitability_report = object()
        manufacturing_package = object()
        manufacturing_production_package = object()
        manufacturing_metrics_report = object()
        factory_decision_report = object()
        joinery_report = object()
        call_manager = MagicMock()

        summary_builder_class.return_value.build.return_value = project_summary
        quotation_builder_class.return_value.build.return_value = quotation_document
        breakdown_builder_class.return_value.build.return_value = (
            quotation_breakdowns
        )
        profitability_builder_class.return_value.build.return_value = (
            profitability_report
        )
        complexity_builder_class.return_value.build.return_value = (
            manufacturing_complexity_report
        )
        duration_builder_class.return_value.build.return_value = (
            manufacturing_duration_report
        )
        capacity_builder_class.return_value.build.return_value = (
            manufacturing_capacity_report
        )
        call_manager.attach_mock(
            complexity_builder_class.return_value.build,
            "complexity_build",
        )
        call_manager.attach_mock(
            duration_builder_class.return_value.build,
            "duration_build",
        )
        call_manager.attach_mock(
            capacity_builder_class.return_value.build,
            "capacity_build",
        )
        project_package_builder_class.return_value.build.return_value = (
            manufacturing_package
        )
        production_package_builder_class.return_value.build.return_value = (
            manufacturing_production_package
        )
        metrics_builder_class.return_value.build.return_value = (
            manufacturing_metrics_report
        )
        decision_builder_class.return_value.build.return_value = (
            factory_decision_report
        )
        joinery_builder_class.return_value.build.return_value = joinery_report

        result = FurnitureProjectBusinessReportBuilder().build(
            furniture_project,
            quotation_number="Q-001",
            issue_date="2026-06-15",
            valid_until="2026-07-15",
            seller_name="Smart Furniture",
            customer_name="Example Customer",
            project_description="Kitchen project",
            markup_rate=0.25,
            currency="EUR",
            notes="Installation included",
            payment_terms="50% deposit",
        )

        self.assertIsInstance(result, FurnitureProjectBusinessReport)
        self.assertIs(result.project_summary, project_summary)
        self.assertIs(result.quotation_document, quotation_document)
        self.assertIs(result.quotation_breakdowns, quotation_breakdowns)
        self.assertIs(
            result.manufacturing_metrics_report,
            manufacturing_metrics_report,
        )
        self.assertIs(
            result.manufacturing_complexity_report,
            manufacturing_complexity_report,
        )
        self.assertIs(
            result.manufacturing_duration_report,
            manufacturing_duration_report,
        )
        self.assertIs(
            result.manufacturing_capacity_report,
            manufacturing_capacity_report,
        )
        self.assertIs(result.profitability_report, profitability_report)
        self.assertIsNone(result.executive_report)
        self.assertIs(result.factory_decision_report, factory_decision_report)

        summary_builder_class.return_value.build.assert_called_once_with(
            furniture_project
        )
        quotation_builder_class.return_value.build.assert_called_once_with(
            furniture_project,
            quotation_number="Q-001",
            issue_date="2026-06-15",
            valid_until="2026-07-15",
            seller_name="Smart Furniture",
            customer_name="Example Customer",
            project_description="Kitchen project",
            markup_rate=0.25,
            currency="EUR",
            notes="Installation included",
            payment_terms="50% deposit",
        )
        breakdown_builder_class.return_value.build.assert_called_once_with(
            furniture_project,
            markup_rate=0.25,
            currency="EUR",
        )
        profitability_builder_class.return_value.build.assert_called_once_with(
            furniture_project,
            markup_rate=0.25,
            currency="EUR",
        )
        project_package_builder_class.return_value.build.assert_called_once_with(
            furniture_project
        )
        production_package_builder_class.return_value.build.assert_called_once_with(
            manufacturing_package
        )
        metrics_builder_class.return_value.build.assert_called_once_with(
            manufacturing_production_package
        )
        complexity_builder_class.return_value.build.assert_called_once_with(
            manufacturing_metrics_report,
            joinery_report=joinery_report,
        )
        duration_builder_class.return_value.build.assert_called_once_with(
            manufacturing_metrics_report
        )
        capacity_builder_class.return_value.build.assert_called_once_with(
            manufacturing_duration_report
        )
        decision_builder_class.return_value.build.assert_called_once_with(
            furniture_project,
            markup_rate=0.25,
            currency="EUR",
        )
        joinery_builder_class.return_value.build.assert_called_once_with(
            furniture_project
        )

        self.assertEqual(
            call_manager.mock_calls[:3],
            [
                call.complexity_build(
                    manufacturing_metrics_report,
                    joinery_report=joinery_report,
                ),
                call.duration_build(manufacturing_metrics_report),
                call.capacity_build(manufacturing_duration_report),
            ],
        )

    def test_builder_exists_with_defaults(self):
        from cost_intelligence.furniture_project_business_report_builder import (
            FurnitureProjectBusinessReportBuilder,
        )

        self.assertTrue(callable(FurnitureProjectBusinessReportBuilder().build))


if __name__ == "__main__":
    unittest.main()
