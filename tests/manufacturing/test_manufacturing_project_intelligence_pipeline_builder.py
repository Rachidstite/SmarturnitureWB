import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace
from unittest.mock import patch


class TestManufacturingProjectIntelligencePipelineBuilder(unittest.TestCase):

    def test_project_result_is_dataclass_with_exact_field_order(self):
        from manufacturing.manufacturing_project_intelligence_result import (
            ManufacturingProjectIntelligenceResult,
        )

        self.assertTrue(is_dataclass(ManufacturingProjectIntelligenceResult))
        self.assertEqual(
            [
                field.name
                for field in fields(ManufacturingProjectIntelligenceResult)
            ],
            [
                "manufacturing_runtime_result",
                "manufacturing_factory_intelligence_result",
            ],
        )

    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "ConsumptionReport"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "CostEstimate"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "SceneGraphCostService"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "SheetUtilizationBuilder"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "IndustrialNestingEngine"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "GuillotineStripStrategy"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "CutListEngine"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "ManufacturingFactoryIntelligencePipelineBuilder"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "ManufacturingRuntimePipelineBuilder"
    )
    def test_pipeline_delegates_and_returns_both_results(
        self,
        runtime_builder_class,
        factory_builder_class,
        cutlist_engine_class,
        strategy_class,
        nesting_engine_class,
        sheet_utilization_builder_class,
        scene_graph_cost_service_class,
        cost_estimate_class,
        consumption_report_class,
    ):
        from manufacturing.manufacturing_project_intelligence_pipeline_builder import (
            ManufacturingProjectIntelligencePipelineBuilder,
        )
        from manufacturing.manufacturing_project_intelligence_result import (
            ManufacturingProjectIntelligenceResult,
        )

        scene_graph = object()
        production_package = object()
        runtime_result = SimpleNamespace(
            manufacturing_production_package=production_package
        )
        cutlist_items = [object()]
        sheet_results = [object()]
        sheet_utilization_report = SimpleNamespace(
            waste_rate=0.42,
            warnings=["sheet-warning"],
        )
        cost_report = SimpleNamespace(
            waste_cost=88.0,
            warnings=["cost-warning"],
        )
        consumption_report = object()
        cost_estimate = object()
        factory_result = object()

        runtime_builder_class.return_value.build.return_value = runtime_result
        cutlist_engine_class.extract.return_value = cutlist_items
        strategy_class.return_value = object()
        nesting_engine_class.return_value.process.return_value = sheet_results
        sheet_utilization_builder_class.return_value.build.return_value = (
            sheet_utilization_report
        )
        scene_graph_cost_service_class.estimate.return_value = cost_report
        cost_estimate_class.return_value = cost_estimate
        consumption_report_class.return_value = consumption_report
        factory_builder_class.return_value.build.return_value = factory_result

        result = ManufacturingProjectIntelligencePipelineBuilder().build(
            scene_graph,
            markup_rate=0.25,
            currency="EUR",
        )

        runtime_builder_class.return_value.build.assert_called_once_with(
            scene_graph
        )
        cutlist_engine_class.extract.assert_called_once_with(scene_graph)
        nesting_engine_class.return_value.process.assert_called_once_with(
            cutlist_items
        )
        sheet_utilization_builder_class.return_value.build.assert_called_once_with(
            sheet_results
        )
        scene_graph_cost_service_class.estimate.assert_called_once_with(
            scene_graph
        )
        cost_estimate_class.assert_called_once_with(
            waste_cost=88.0,
            warnings=["cost-warning", "sheet-warning"],
        )
        consumption_report_class.assert_called_once_with(
            waste_ratio=0.42,
            warnings=["cost-warning", "sheet-warning"],
        )
        factory_builder_class.return_value.build.assert_called_once_with(
            production_package,
            0.25,
            "EUR",
            sheet_results=sheet_results,
            consumption_report=consumption_report,
            cost_estimate=cost_estimate,
        )
        self.assertIsInstance(result, ManufacturingProjectIntelligenceResult)
        self.assertIs(result.manufacturing_runtime_result, runtime_result)
        self.assertIs(
            result.manufacturing_factory_intelligence_result,
            factory_result,
        )

    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "ConsumptionReport"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "CostEstimate"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "SceneGraphCostService"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "SheetUtilizationBuilder"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "IndustrialNestingEngine"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "GuillotineStripStrategy"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "CutListEngine"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "ManufacturingFactoryIntelligencePipelineBuilder"
    )
    @patch(
        "manufacturing.manufacturing_project_intelligence_pipeline_builder."
        "ManufacturingRuntimePipelineBuilder"
    )
    def test_pipeline_uses_defaults_and_does_not_mutate_scene_graph(
        self,
        runtime_builder_class,
        factory_builder_class,
        cutlist_engine_class,
        strategy_class,
        nesting_engine_class,
        sheet_utilization_builder_class,
        scene_graph_cost_service_class,
        cost_estimate_class,
        consumption_report_class,
    ):
        from manufacturing.manufacturing_project_intelligence_pipeline_builder import (
            ManufacturingProjectIntelligencePipelineBuilder,
        )
        from scene_graph.scene_graph import SceneGraph

        scene_graph = SceneGraph()
        original_nodes = scene_graph.nodes
        original_identity_map = scene_graph._identity_map
        production_package = object()
        runtime_builder_class.return_value.build.return_value = SimpleNamespace(
            manufacturing_production_package=production_package
        )
        cutlist_engine_class.extract.return_value = []
        strategy_class.return_value = object()
        nesting_engine_class.return_value.process.return_value = []
        sheet_utilization_builder_class.return_value.build.return_value = (
            SimpleNamespace(waste_rate=0.0, warnings=[])
        )
        scene_graph_cost_service_class.estimate.return_value = SimpleNamespace(
            waste_cost=0.0,
            warnings=[],
        )
        cost_estimate_class.return_value = SimpleNamespace(
            waste_cost=0.0,
            warnings=[],
        )
        consumption_report_class.return_value = SimpleNamespace(
            waste_ratio=0.0,
            warnings=[],
        )

        ManufacturingProjectIntelligencePipelineBuilder().build(scene_graph)

        factory_builder_class.return_value.build.assert_called_once_with(
            production_package,
            0.0,
            "MAD",
            sheet_results=[],
            consumption_report=consumption_report_class.return_value,
            cost_estimate=cost_estimate_class.return_value,
        )
        self.assertIs(scene_graph.nodes, original_nodes)
        self.assertIs(scene_graph._identity_map, original_identity_map)
        self.assertEqual(scene_graph.nodes, [])
        self.assertEqual(scene_graph._identity_map, {})


if __name__ == "__main__":
    unittest.main()
