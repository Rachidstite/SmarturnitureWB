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
        factory_result = object()
        runtime_builder_class.return_value.build.return_value = runtime_result
        factory_builder_class.return_value.build.return_value = factory_result

        result = ManufacturingProjectIntelligencePipelineBuilder().build(
            scene_graph,
            markup_rate=0.25,
            currency="EUR",
        )

        runtime_builder_class.return_value.build.assert_called_once_with(
            scene_graph
        )
        factory_builder_class.return_value.build.assert_called_once_with(
            production_package,
            0.25,
            "EUR",
        )
        self.assertIsInstance(result, ManufacturingProjectIntelligenceResult)
        self.assertIs(result.manufacturing_runtime_result, runtime_result)
        self.assertIs(
            result.manufacturing_factory_intelligence_result,
            factory_result,
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

        ManufacturingProjectIntelligencePipelineBuilder().build(scene_graph)

        factory_builder_class.return_value.build.assert_called_once_with(
            production_package,
            0.0,
            "MAD",
        )
        self.assertIs(scene_graph.nodes, original_nodes)
        self.assertIs(scene_graph._identity_map, original_identity_map)
        self.assertEqual(scene_graph.nodes, [])
        self.assertEqual(scene_graph._identity_map, {})


if __name__ == "__main__":
    unittest.main()
