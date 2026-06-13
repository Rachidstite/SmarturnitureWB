import unittest
from dataclasses import fields, is_dataclass
from unittest.mock import patch


class TestManufacturingRuntimePipelineBuilder(unittest.TestCase):

    def test_runtime_result_is_dataclass_with_exact_field_order(self):
        from manufacturing.manufacturing_runtime_result import (
            ManufacturingRuntimeResult,
        )

        self.assertTrue(is_dataclass(ManufacturingRuntimeResult))
        self.assertEqual(
            [field.name for field in fields(ManufacturingRuntimeResult)],
            [
                "panel_specs",
                "manufacturing_package",
                "manufacturing_production_package",
            ],
        )

    @patch(
        "manufacturing.manufacturing_runtime_pipeline_builder."
        "ManufacturingProductionPackageBuilder"
    )
    @patch(
        "manufacturing.manufacturing_runtime_pipeline_builder."
        "ManufacturingPackageBuilder"
    )
    @patch(
        "manufacturing.manufacturing_runtime_pipeline_builder."
        "ManufacturingExtractor"
    )
    def test_pipeline_builds_runtime_results_from_extracted_panels(
        self,
        extractor,
        package_builder_class,
        production_package_builder_class,
    ):
        from manufacturing.edge_spec import EdgeSpec
        from manufacturing.manufacturing_runtime_pipeline_builder import (
            ManufacturingRuntimePipelineBuilder,
        )
        from manufacturing.manufacturing_runtime_result import (
            ManufacturingRuntimeResult,
        )
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )

        first_cnc_operation = object()
        second_cnc_operation = object()
        panel_specs = [
            self._panel(
                cnc_operations=[first_cnc_operation],
                edge_spec=EdgeSpec(top="ABS_1MM", right="PVC_2MM"),
            ),
            self._panel(
                cnc_operations=[second_cnc_operation],
                edge_spec=EdgeSpec(bottom="ABS_1MM"),
            ),
        ]
        scene_graph = object()
        manufacturing_package = object()
        manufacturing_production_package = object()

        extractor.extract.return_value = panel_specs
        package_builder_class.return_value.build.return_value = (
            manufacturing_package
        )
        production_package_builder_class.return_value.build.return_value = (
            manufacturing_production_package
        )

        result = ManufacturingRuntimePipelineBuilder().build(scene_graph)

        extractor.extract.assert_called_once_with(scene_graph)
        package_builder_class.return_value.build.assert_called_once()
        build_kwargs = package_builder_class.return_value.build.call_args.kwargs
        self.assertIs(build_kwargs["panels"], panel_specs)
        self.assertEqual(build_kwargs["materials"], [])
        self.assertEqual(
            build_kwargs["machining_operations"],
            [first_cnc_operation, second_cnc_operation],
        )
        self.assertEqual(build_kwargs["warnings"], [])
        self.assertEqual(len(build_kwargs["edge_operations"]), 3)
        self.assertTrue(
            all(
                isinstance(operation, UnifiedManufacturingOperation)
                for operation in build_kwargs["edge_operations"]
            )
        )
        self.assertTrue(
            all(
                operation.operation_type == "EDGE_BANDING"
                for operation in build_kwargs["edge_operations"]
            )
        )
        production_package_builder_class.return_value.build.assert_called_once_with(
            manufacturing_package
        )
        self.assertIsInstance(result, ManufacturingRuntimeResult)
        self.assertIs(result.panel_specs, panel_specs)
        self.assertIs(result.manufacturing_package, manufacturing_package)
        self.assertIs(
            result.manufacturing_production_package,
            manufacturing_production_package,
        )

    @patch(
        "manufacturing.manufacturing_runtime_pipeline_builder."
        "ManufacturingProductionPackageBuilder"
    )
    @patch(
        "manufacturing.manufacturing_runtime_pipeline_builder."
        "ManufacturingPackageBuilder"
    )
    @patch(
        "manufacturing.manufacturing_runtime_pipeline_builder."
        "ManufacturingExtractor"
    )
    def test_pipeline_does_not_mutate_scene_graph(
        self,
        extractor,
        package_builder_class,
        production_package_builder_class,
    ):
        from manufacturing.manufacturing_runtime_pipeline_builder import (
            ManufacturingRuntimePipelineBuilder,
        )
        from scene_graph.scene_graph import SceneGraph

        scene_graph = SceneGraph()
        original_nodes = scene_graph.nodes
        original_identity_map = scene_graph._identity_map
        extractor.extract.return_value = []

        ManufacturingRuntimePipelineBuilder().build(scene_graph)

        self.assertIs(scene_graph.nodes, original_nodes)
        self.assertIs(scene_graph._identity_map, original_identity_map)
        self.assertEqual(scene_graph.nodes, [])
        self.assertEqual(scene_graph._identity_map, {})

    @staticmethod
    def _panel(cnc_operations, edge_spec):
        from types import SimpleNamespace

        return SimpleNamespace(
            cnc_operations=cnc_operations,
            edge_spec=edge_spec,
        )


if __name__ == "__main__":
    unittest.main()
