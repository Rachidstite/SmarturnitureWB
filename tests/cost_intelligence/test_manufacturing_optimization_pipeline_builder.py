import unittest
from dataclasses import fields, is_dataclass
from unittest.mock import patch


class TestManufacturingOptimizationPipelineBuilder(unittest.TestCase):

    def test_optimization_result_is_dataclass_with_required_fields(self):
        from cost_intelligence.manufacturing_optimization_result import (
            ManufacturingOptimizationResult,
        )

        self.assertTrue(is_dataclass(ManufacturingOptimizationResult))
        self.assertEqual(
            [field.name for field in fields(ManufacturingOptimizationResult)],
            [
                "sheet_utilization_report",
                "offcut_report",
                "offcut_intelligence_report",
                "waste_intelligence_report",
                "nesting_intelligence_report",
            ],
        )

    def test_builder_exists(self):
        from cost_intelligence.manufacturing_optimization_pipeline_builder import (
            ManufacturingOptimizationPipelineBuilder,
        )

        self.assertTrue(
            callable(ManufacturingOptimizationPipelineBuilder().build)
        )

    @patch(
        "cost_intelligence.manufacturing_optimization_pipeline_builder."
        "NestingIntelligenceBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_optimization_pipeline_builder."
        "WasteIntelligenceBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_optimization_pipeline_builder."
        "OffcutIntelligenceBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_optimization_pipeline_builder."
        "OffcutReportBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_optimization_pipeline_builder."
        "OffcutExtractionService"
    )
    @patch(
        "cost_intelligence.manufacturing_optimization_pipeline_builder."
        "SheetUtilizationBuilder"
    )
    def test_build_orchestrates_existing_components(
        self,
        sheet_utilization_builder_class,
        offcut_extraction_service,
        offcut_report_builder_class,
        offcut_intelligence_builder_class,
        waste_intelligence_builder_class,
        nesting_intelligence_builder_class,
    ):
        from cost_intelligence.manufacturing_optimization_pipeline_builder import (
            ManufacturingOptimizationPipelineBuilder,
        )
        from cost_intelligence.manufacturing_optimization_result import (
            ManufacturingOptimizationResult,
        )

        sheet_results = object()
        consumption_report = object()
        cost_estimate = object()
        sheet_utilization_report = object()
        offcuts = object()
        offcut_report = object()
        offcut_intelligence_report = object()
        waste_intelligence_report = object()
        nesting_intelligence_report = object()

        sheet_utilization_builder_class.return_value.build.return_value = (
            sheet_utilization_report
        )
        offcut_extraction_service.extract.return_value = offcuts
        offcut_report_builder_class.return_value.build.return_value = (
            offcut_report
        )
        offcut_intelligence_builder_class.return_value.build.return_value = (
            offcut_intelligence_report
        )
        waste_intelligence_builder_class.return_value.build.return_value = (
            waste_intelligence_report
        )
        nesting_intelligence_builder_class.return_value.build.return_value = (
            nesting_intelligence_report
        )

        result = ManufacturingOptimizationPipelineBuilder().build(
            sheet_results,
            consumption_report,
            cost_estimate,
        )

        self.assertIsInstance(result, ManufacturingOptimizationResult)
        self.assertIs(result.sheet_utilization_report, sheet_utilization_report)
        self.assertIs(result.offcut_report, offcut_report)
        self.assertIs(result.offcut_intelligence_report, offcut_intelligence_report)
        self.assertIs(result.waste_intelligence_report, waste_intelligence_report)
        self.assertIs(
            result.nesting_intelligence_report,
            nesting_intelligence_report,
        )
        sheet_utilization_builder_class.return_value.build.assert_called_once_with(
            sheet_results
        )
        offcut_extraction_service.extract.assert_called_once_with(sheet_results)
        offcut_report_builder_class.return_value.build.assert_called_once_with(
            offcuts
        )
        offcut_intelligence_builder_class.return_value.build.assert_called_once_with(
            offcut_report
        )
        waste_intelligence_builder_class.return_value.build.assert_called_once_with(
            consumption_report,
            cost_estimate,
            offcut_intelligence_report,
        )
        nesting_intelligence_builder_class.return_value.build.assert_called_once_with(
            sheet_utilization_report,
            offcut_intelligence_report,
            waste_intelligence_report,
        )


if __name__ == "__main__":
    unittest.main()
