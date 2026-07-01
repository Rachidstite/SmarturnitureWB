import inspect
import unittest
from importlib import import_module
from types import ModuleType
from unittest.mock import patch

import scene_graph.scene_graph as scene_graph_module
from engine.geometry_engine import GeometryEngine
from scene_graph.builder import SceneGraphBuilder


class TestExecutionBoundaryContracts(unittest.TestCase):
    @staticmethod
    def _import_cabinet_builder_module():
        fake_freecad = ModuleType("FreeCAD")
        fake_part = ModuleType("Part")
        fake_freecad_gui = ModuleType("FreeCADGui")

        with patch.dict(
            "sys.modules",
            {
                "FreeCAD": fake_freecad,
                "Part": fake_part,
                "FreeCADGui": fake_freecad_gui,
            },
        ):
            return import_module("engine.cabinet_builder")

    def test_cabinet_builder_is_geometry_execution_boundary(self):
        cabinet_builder_module = self._import_cabinet_builder_module()
        signature = inspect.signature(cabinet_builder_module.CabinetBuilder.build)

        self.assertEqual(list(signature.parameters), ["self", "cabinet"])

        source = inspect.getsource(cabinet_builder_module)
        for token in (
            "ManufacturingRuntimePipelineBuilder",
            "ManufacturingPackageBuilder",
            "ManufacturingProductionPackageBuilder",
            "CostPackageBuilder",
            "CommercialPackageBuilder",
            "ProductFamily",
            "ProductConfiguration",
        ):
            self.assertNotIn(token, source)

    def test_geometry_engine_produces_geometry_only(self):
        signature = inspect.signature(GeometryEngine.resolve_all)
        self.assertEqual(list(signature.parameters), ["self"])

        source = inspect.getsource(import_module("engine.geometry_engine"))
        for token in (
            "ProductFamily",
            "ProductConfiguration",
            "ManufacturingRuntimePipelineBuilder",
            "ManufacturingPackageBuilder",
            "ManufacturingProductionPackageBuilder",
            "CostPackageBuilder",
            "CommercialPackageBuilder",
        ):
            self.assertNotIn(token, source)

    def test_scene_graph_builder_consumes_geometry_only(self):
        signature = inspect.signature(SceneGraphBuilder.build)
        self.assertEqual(list(signature.parameters), ["self", "geo"])

        source = inspect.getsource(import_module("scene_graph.builder"))
        for token in ("ProductFamily", "ProductConfiguration"):
            self.assertNotIn(token, source)

    def test_scene_graph_has_no_product_family_semantics(self):
        source = inspect.getsource(scene_graph_module)
        for token in ("ProductFamily", "ProductConfiguration"):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
