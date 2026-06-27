import unittest
from dataclasses import fields, is_dataclass
from unittest.mock import patch


class TestManufacturingCommercialPipelineBuilder(unittest.TestCase):

    def test_commercial_result_is_dataclass_with_required_fields(self):
        from cost_intelligence.manufacturing_commercial_result import (
            ManufacturingCommercialResult,
        )

        self.assertTrue(is_dataclass(ManufacturingCommercialResult))
        self.assertEqual(
            [field.name for field in fields(ManufacturingCommercialResult)],
            [
                "manufacturing_cost_summary",
                "manufacturing_quotation_input",
                "quotation_report",
                "profitability_report",
                "quotation_intelligence_report",
            ],
        )

    def test_builder_exists(self):
        from cost_intelligence.manufacturing_commercial_pipeline_builder import (
            ManufacturingCommercialPipelineBuilder,
        )

        self.assertTrue(callable(ManufacturingCommercialPipelineBuilder().build))

    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "QuotationIntelligenceBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "ManufacturingProfitabilityReportBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "ManufacturingQuotationReportBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "ManufacturingQuotationInputBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "ManufacturingCostPipelineBuilder"
    )
    def test_build_orchestrates_existing_builders(
        self,
        cost_builder_class,
        quotation_input_builder_class,
        quotation_report_builder_class,
        profitability_report_builder_class,
        quotation_intelligence_builder_class,
    ):
        from cost_intelligence.manufacturing_commercial_result import (
            ManufacturingCommercialResult,
        )
        from cost_intelligence.manufacturing_commercial_pipeline_builder import (
            ManufacturingCommercialPipelineBuilder,
        )

        production_package = object()
        cost_summary = object()
        quotation_input = object()
        quotation_report = object()
        profitability_report = object()
        quotation_intelligence_report = object()

        cost_builder_class.return_value.build.return_value = cost_summary
        quotation_input_builder_class.return_value.build.return_value = (
            quotation_input
        )
        quotation_report_builder_class.return_value.build.return_value = (
            quotation_report
        )
        profitability_report_builder_class.return_value.build.return_value = (
            profitability_report
        )
        quotation_intelligence_builder_class.return_value.build.return_value = (
            quotation_intelligence_report
        )

        result = ManufacturingCommercialPipelineBuilder().build(
            production_package,
            markup_rate=0.25,
            currency="EUR",
        )

        self.assertIsInstance(result, ManufacturingCommercialResult)
        self.assertIs(result.manufacturing_cost_summary, cost_summary)
        self.assertIs(result.manufacturing_quotation_input, quotation_input)
        self.assertIs(result.quotation_report, quotation_report)
        self.assertIs(result.profitability_report, profitability_report)
        self.assertIs(
            result.quotation_intelligence_report,
            quotation_intelligence_report,
        )
        cost_builder_class.return_value.build.assert_called_once_with(
            production_package
        )
        quotation_input_builder_class.return_value.build.assert_called_once_with(
            cost_summary,
            markup_rate=0.25,
            currency="EUR",
        )
        quotation_report_builder_class.return_value.build.assert_called_once_with(
            quotation_input
        )
        profitability_report_builder_class.return_value.build.assert_called_once_with(
            quotation_report
        )
        quotation_intelligence_builder_class.return_value.build.assert_called_once_with(
            quotation_report,
            profitability_report,
        )

    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "QuotationIntelligenceBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "ManufacturingProfitabilityReportBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "ManufacturingQuotationReportBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "ManufacturingQuotationInputBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "ManufacturingCostPipelineBuilder"
    )
    def test_build_reuses_precomputed_cost_summary(
        self,
        cost_builder_class,
        quotation_input_builder_class,
        quotation_report_builder_class,
        profitability_report_builder_class,
        quotation_intelligence_builder_class,
    ):
        from cost_intelligence.manufacturing_commercial_pipeline_builder import (
            ManufacturingCommercialPipelineBuilder,
        )

        production_package = object()
        cost_summary = object()
        quotation_input = object()
        quotation_report = object()
        profitability_report = object()
        quotation_intelligence_report = object()

        quotation_input_builder_class.return_value.build.return_value = (
            quotation_input
        )
        quotation_report_builder_class.return_value.build.return_value = (
            quotation_report
        )
        profitability_report_builder_class.return_value.build.return_value = (
            profitability_report
        )
        quotation_intelligence_builder_class.return_value.build.return_value = (
            quotation_intelligence_report
        )

        result = ManufacturingCommercialPipelineBuilder().build(
            production_package,
            markup_rate=0.25,
            currency="EUR",
            manufacturing_cost_summary=cost_summary,
        )

        self.assertIs(result.manufacturing_cost_summary, cost_summary)
        cost_builder_class.return_value.build.assert_not_called()
        quotation_input_builder_class.return_value.build.assert_called_once_with(
            cost_summary,
            markup_rate=0.25,
            currency="EUR",
        )

    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "QuotationIntelligenceBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "ManufacturingProfitabilityReportBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "ManufacturingQuotationReportBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "ManufacturingQuotationInputBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_commercial_pipeline_builder."
        "ManufacturingCostPipelineBuilder"
    )
    def test_build_uses_commercial_defaults(
        self,
        cost_builder_class,
        quotation_input_builder_class,
        quotation_report_builder_class,
        profitability_report_builder_class,
        quotation_intelligence_builder_class,
    ):
        from cost_intelligence.manufacturing_commercial_pipeline_builder import (
            ManufacturingCommercialPipelineBuilder,
        )

        production_package = object()
        cost_summary = object()
        cost_builder_class.return_value.build.return_value = cost_summary

        ManufacturingCommercialPipelineBuilder().build(production_package)

        quotation_input_builder_class.return_value.build.assert_called_once_with(
            cost_summary,
            markup_rate=0.0,
            currency="MAD",
        )


if __name__ == "__main__":
    unittest.main()
