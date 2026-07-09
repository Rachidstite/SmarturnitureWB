import inspect
import unittest
from dataclasses import fields, is_dataclass
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as engineering_entry_module
import domain.base_cabinet_engineering_model as engineering_model_module
import domain.construction_resolver as resolver_module
import domain.furniture_construction_model as construction_module
from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
    build_base_cabinet_engineering_cabinet,
)
from domain.base_cabinet_engineering_model import BaseCabinetEngineeringModel
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.construction_resolver import ConstructionResolver
from domain.furniture_construction_model import CabinetConstructionModel
from engine.cabinet import Cabinet


class FakeCabinetBuilder:
    def __init__(self):
        self.scene_graph = object()

    def build(self, cabinet):
        cabinet.graph = self.scene_graph
        cabinet.scene_graph = self.scene_graph


class MissingSceneGraphCabinetBuilder:
    def __init__(self):
        self.scene_graph = None

    def build(self, cabinet):
        cabinet.graph = None
        cabinet.scene_graph = None


class TestExecutionBoundaryContracts(unittest.TestCase):
    def test_engineering_entry_attaches_engineering_model_without_geometry(self):
        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            cabinet = build_base_cabinet_engineering_cabinet(
                BaseCabinetSpecification()
            )

        self.assertIsInstance(cabinet, Cabinet)
        self.assertIsInstance(cabinet.engineering_model, BaseCabinetEngineeringModel)
        self.assertIsInstance(cabinet.construction_model, CabinetConstructionModel)
        self.assertFalse(hasattr(cabinet.engineering_model, "scene_graph"))
        self.assertFalse(hasattr(cabinet.engineering_model, "geometry"))
        self.assertFalse(hasattr(cabinet.engineering_model, "manufacturing_package"))

        source = inspect.getsource(engineering_model_module)
        for token in (
            "SceneGraph",
            "GeometryEngine",
            "ManufacturingRuntimePipelineBuilder",
            "ManufacturingPackageBuilder",
            "ProductFamily",
        ):
            self.assertNotIn(token, source)

    def test_engineering_model_contains_no_geometry_objects(self):
        self.assertTrue(is_dataclass(BaseCabinetEngineeringModel))
        field_names = {field.name for field in fields(BaseCabinetEngineeringModel)}
        for forbidden in (
            "scene_graph",
            "geometry",
            "manufacturing_package",
            "manufacturing_production_package",
        ):
            self.assertNotIn(forbidden, field_names)

    def test_construction_resolver_returns_only_construction_model(self):
        model = ConstructionResolver.resolve(BaseCabinetSpecification())

        self.assertIsInstance(model, CabinetConstructionModel)
        self.assertFalse(hasattr(model, "scene_graph"))
        self.assertFalse(hasattr(model, "geometry"))
        self.assertFalse(hasattr(model, "manufacturing_package"))

        source = inspect.getsource(resolver_module)
        for token in (
            "SceneGraph",
            "GeometryEngine",
            "ManufacturingRuntimePipelineBuilder",
            "ManufacturingPackageBuilder",
            "ProductFamily",
        ):
            self.assertNotIn(token, source)

    def test_construction_model_contains_no_scene_graph(self):
        model = CabinetConstructionModel.reference_base_cabinet()

        self.assertFalse(hasattr(model, "scene_graph"))
        self.assertFalse(hasattr(model, "geometry"))
        self.assertFalse(hasattr(model, "graph"))

        field_names = {field.name for field in fields(CabinetConstructionModel)}
        for forbidden in ("scene_graph", "geometry", "graph"):
            self.assertNotIn(forbidden, field_names)

        source = inspect.getsource(construction_module)
        for token in ("SceneGraph", "GeometryEngine", "ProductFamily"):
            self.assertNotIn(token, source)

    def test_engineering_entry_success_always_exposes_scene_graph(self):
        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            cabinet = build_base_cabinet_engineering_cabinet(
                BaseCabinetSpecification()
            )

        self.assertTrue(hasattr(cabinet, "graph"))
        self.assertTrue(hasattr(cabinet, "scene_graph"))
        self.assertIsNotNone(cabinet.graph)
        self.assertIs(cabinet.graph, cabinet.scene_graph)

    def test_missing_scene_graph_cannot_escape_engineering_boundary(self):
        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=MissingSceneGraphCabinetBuilder,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "did not produce a scene graph",
            ):
                build_base_cabinet_engineering_cabinet(
                    BaseCabinetSpecification()
                )


if __name__ == "__main__":
    unittest.main()
