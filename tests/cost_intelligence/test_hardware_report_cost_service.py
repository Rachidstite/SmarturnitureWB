import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch


class TestHardwareReportCostService(unittest.TestCase):

    def test_service_exists(self):
        from cost_intelligence.hardware_report_cost_service import (
            HardwareReportCostService,
        )

        self.assertTrue(callable(HardwareReportCostService.estimate))

    @patch("exports.hardware_report.AssemblyGraphBuilder")
    def test_hardware_report_generate_keeps_hardware_cost_zero(
        self,
        assembly_graph_builder,
    ):
        from exports.hardware_report import HardwareReportEngine

        assembly_graph_builder.build.return_value = SimpleNamespace(
            all_joints=lambda: [
                SimpleNamespace(joint_type="MINIFIX"),
                SimpleNamespace(joint_type="HINGE"),
            ]
        )

        report = HardwareReportEngine.generate(object())

        self.assertEqual(report.minifix_count, 3)
        self.assertEqual(report.dowel_count, 2)
        self.assertEqual(report.hinge_count, 4)
        self.assertEqual(report.hardware_cost, 0.0)

    def test_estimate_from_project_prices_all_hardware_families(
        self,
    ):
        from cost_intelligence.hardware_report_cost_service import (
            HardwareReportCostService,
        )

        project = SimpleNamespace(
            placements=[
                SimpleNamespace(hardware_intent="INTENT_HINGE"),
                SimpleNamespace(hardware_intent="INTENT_HINGE"),
                SimpleNamespace(hardware_intent="INTENT_MINIFIX_15"),
                SimpleNamespace(hardware_intent="INTENT_CONFIRMAT_50"),
                SimpleNamespace(hardware_intent="INTENT_SHELF_PIN"),
                SimpleNamespace(hardware_intent="INTENT_SHELF_PIN"),
                SimpleNamespace(hardware_intent="INTENT_SHELF_PIN"),
            ]
        )
        context = SimpleNamespace(
            hardware_profile={
                "INTENT_HINGE": "HINGE_BLUM_110_V1",
                "INTENT_MINIFIX_15": "MINIFIX_15_V1",
                "INTENT_CONFIRMAT_50": "CONFIRMAT_50_V1",
                "INTENT_SHELF_PIN": "SHELF_PIN_5MM",
            }
        )
        pricing_catalog = {
            "HINGE_BLUM_110_V1": {"unit_price": 6.0},
            "MINIFIX_15_V1": {"unit_price": 1.5},
            "CONFIRMAT_50_V1": {"unit_price": 2.0},
            "SHELF_PIN_5MM": {"unit_price": 0.5},
        }

        result = HardwareReportCostService.estimate_from_project(
            project,
            context,
            pricing_catalog=pricing_catalog,
        )

        self.assertEqual(result.hardware_cost, 17.0)
        self.assertEqual(result.total_cost, 17.0)

    def test_estimate_from_project_surfaces_missing_price_warnings(
        self,
    ):
        from cost_intelligence.hardware_report_cost_service import (
            HardwareReportCostService,
        )

        project = SimpleNamespace(
            placements=[
                SimpleNamespace(hardware_intent="INTENT_HINGE"),
                SimpleNamespace(hardware_intent="INTENT_MINIFIX_15"),
                SimpleNamespace(hardware_intent="INTENT_CONFIRMAT_50"),
                SimpleNamespace(hardware_intent="INTENT_SHELF_PIN"),
            ]
        )
        context = SimpleNamespace(
            hardware_profile={
                "INTENT_HINGE": "HINGE_BLUM_110_V1",
                "INTENT_MINIFIX_15": "MINIFIX_15_V1",
                "INTENT_CONFIRMAT_50": "CONFIRMAT_50_V1",
                "INTENT_SHELF_PIN": "SHELF_PIN_5MM",
            }
        )
        pricing_catalog = {
            "HINGE_BLUM_110_V1": {"unit_price": 6.0},
        }

        result = HardwareReportCostService.estimate_from_project(
            project,
            context,
            pricing_catalog=pricing_catalog,
        )

        self.assertEqual(
            result.warnings,
            [
                "Missing hardware price for MINIFIX_15_V1",
                "Missing hardware price for CONFIRMAT_50_V1",
                "Missing hardware price for SHELF_PIN_5MM",
            ],
        )
        self.assertEqual(result.hardware_cost, 6.0)
        self.assertEqual(result.total_cost, 6.0)

    def test_generate_from_project_counts_placements_by_context_mapping(self):
        from exports.hardware_report import HardwareReportEngine

        project = SimpleNamespace(
            placements=[
                SimpleNamespace(hardware_intent="INTENT_HINGE"),
                SimpleNamespace(hardware_intent="INTENT_HINGE"),
                SimpleNamespace(hardware_intent="INTENT_MINIFIX_15"),
                SimpleNamespace(hardware_intent="INTENT_CONFIRMAT_50"),
                SimpleNamespace(hardware_intent="INTENT_SHELF_PIN"),
                SimpleNamespace(hardware_intent="INTENT_SHELF_PIN"),
            ]
        )
        context = SimpleNamespace(
            hardware_profile={
                "INTENT_HINGE": "HINGE_BLUM_110_V1",
                "INTENT_MINIFIX_15": "MINIFIX_15_V1",
                "INTENT_CONFIRMAT_50": "CONFIRMAT_50_V1",
                "INTENT_SHELF_PIN": "SHELF_PIN_5MM",
            }
        )

        report = HardwareReportEngine.generate_from_project(project, context)

        self.assertEqual(
            report.hardware_items,
            {
                "HINGE": 2,
                "MINIFIX": 1,
                "CONFIRMAT": 1,
                "SHELF_PIN": 2,
                "DOWEL": 0,
            },
        )
        self.assertEqual(report.hinge_count, 2)
        self.assertEqual(report.minifix_count, 1)
        self.assertEqual(report.dowel_count, 0)

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
        "HardwareReportEngine"
    )
    def test_estimate_scene_graph_path_does_not_use_project_path(
        self,
        hardware_report_engine,
    ):
        from cost_intelligence.hardware_report_cost_service import (
            HardwareReportCostService,
        )

        scene_graph = object()
        report = object()
        hardware_report_engine.generate.return_value = report

        HardwareReportCostService.estimate(scene_graph)

        hardware_report_engine.generate_from_project.assert_not_called()

    @patch(
        "cost_intelligence.hardware_report_cost_service."
        "HardwareReportItemsAdapter"
    )
    @patch(
        "cost_intelligence.hardware_report_cost_service."
        "HardwareReportEngine"
    )
    def test_estimate_returns_catalog_based_hardware_cost(
        self,
        hardware_report_engine,
        hardware_report_items_adapter,
    ):
        from cost_intelligence.hardware_report_cost_service import (
            HardwareReportCostService,
        )

        scene_graph = object()
        report = object()
        hardware_report_engine.generate.return_value = report
        hardware_report_items_adapter.from_report.return_value = [
            {"sku": "MINIFIX_15_V1", "quantity": 8},
        ]
        pricing_catalog = {
            "MINIFIX_15_V1": {"unit_price": 1.5},
        }

        result = HardwareReportCostService.estimate(
            scene_graph,
            pricing_catalog=pricing_catalog,
        )

        self.assertEqual(result.hardware_cost, 12.0)
        self.assertEqual(result.total_cost, 12.0)

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
