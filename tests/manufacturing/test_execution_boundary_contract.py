import inspect
import unittest

from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)


class TestManufacturingExecutionBoundaryContracts(unittest.TestCase):
    def test_runtime_pipeline_accepts_scene_graph_only(self):
        signature = inspect.signature(ManufacturingRuntimePipelineBuilder.build)
        self.assertEqual(list(signature.parameters), ["self", "scene_graph"])

    def test_runtime_pipeline_does_not_depend_on_product_family_or_engineering_entry(self):
        source = inspect.getsource(
            ManufacturingRuntimePipelineBuilder
        )

        for token in (
            "ProductFamily",
            "ProductConfiguration",
            "BaseCabinetEngineeringEntry",
            "WallCabinetEngineeringEntry",
            "build_base_cabinet_engineering_cabinet",
            "build_wall_cabinet_engineering_cabinet",
        ):
            self.assertNotIn(token, source)

    def test_runtime_pipeline_produces_runtime_results_from_scene_graph_only(self):
        source = inspect.getsource(
            ManufacturingRuntimePipelineBuilder
        )

        for token in (
            "ManufacturingExtractor",
            "ManufacturingPackageBuilder",
            "ManufacturingProductionPackageBuilder",
        ):
            self.assertIn(token, source)

        for token in (
            "ProductFamily",
            "ProductConfiguration",
            "EngineeringEntry",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
