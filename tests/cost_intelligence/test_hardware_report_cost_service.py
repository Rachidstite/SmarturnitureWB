import copy
import unittest
from unittest.mock import patch


class TestHardwareReportCostService(unittest.TestCase):

    def test_service_exists(self):
        from cost_intelligence.hardware_report_cost_service import (
            HardwareReportCostService,
        )

        self.assertTrue(callable(HardwareReportCostService.estimate))

    @patch(
        "cost_intelligence.hardware_report_cost_service."
        "HardwareCostCalculator"
    )
    @patch(
        "cost_intelligence.hardware_report_cost_service."
        "HardwareReportItemsAdapter"
    )
    @patch(
        "cost_intelligence.hardware_report_cost_service."
        "HardwareReportEngine"
    )
    def test_estimate_orchestrates_hardware_report_cost(
        self,
        hardware_report_engine,
        hardware_report_items_adapter,
        hardware_cost_calculator_class,
    ):
        from cost_intelligence.hardware_report_cost_service import (
            HardwareReportCostService,
        )

        scene_graph = {"nodes": [{"uid": "PANEL-1"}]}
        original_scene_graph = copy.deepcopy(scene_graph)
        pricing_catalog = {"MINIFIX_15_V1": {"unit_price": 1.5}}
        report = object()
        adapted_items = [{"sku": "MINIFIX_15_V1", "quantity": 8}]
        cost_estimate = object()
        hardware_report_engine.generate.return_value = report
        hardware_report_items_adapter.from_report.return_value = adapted_items
        hardware_cost_calculator_class.return_value.estimate.return_value = (
            cost_estimate
        )

        result = HardwareReportCostService.estimate(
            scene_graph,
            pricing_catalog=pricing_catalog,
        )

        hardware_report_engine.generate.assert_called_once_with(scene_graph)
        hardware_report_items_adapter.from_report.assert_called_once_with(report)
        hardware_cost_calculator_class.return_value.estimate.assert_called_once_with(
            hardware_items=adapted_items,
            pricing_catalog=pricing_catalog,
        )
        passed_pricing_catalog = (
            hardware_cost_calculator_class.return_value.estimate.call_args.kwargs[
                "pricing_catalog"
            ]
        )
        self.assertIs(passed_pricing_catalog, pricing_catalog)
        self.assertIs(result, cost_estimate)
        self.assertEqual(scene_graph, original_scene_graph)

    @patch(
        "cost_intelligence.hardware_report_cost_service."
        "HardwareCostCalculator"
    )
    @patch(
        "cost_intelligence.hardware_report_cost_service."
        "HardwareReportItemsAdapter"
    )
    @patch(
        "cost_intelligence.hardware_report_cost_service."
        "HardwareReportEngine"
    )
    def test_estimate_passes_empty_adapted_items_to_calculator(
        self,
        hardware_report_engine,
        hardware_report_items_adapter,
        hardware_cost_calculator_class,
    ):
        from cost_intelligence.hardware_report_cost_service import (
            HardwareReportCostService,
        )

        scene_graph = object()
        report = object()
        cost_estimate = object()
        hardware_report_engine.generate.return_value = report
        hardware_report_items_adapter.from_report.return_value = []
        hardware_cost_calculator_class.return_value.estimate.return_value = (
            cost_estimate
        )

        result = HardwareReportCostService.estimate(scene_graph)

        hardware_cost_calculator_class.return_value.estimate.assert_called_once_with(
            hardware_items=[],
            pricing_catalog=None,
        )
        self.assertIs(result, cost_estimate)


if __name__ == "__main__":
    unittest.main()
