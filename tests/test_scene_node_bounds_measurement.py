import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass

from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
    measure_scene_node_bounds,
)


class TestSceneNodeBoundsMeasurement(unittest.TestCase):
    def test_measurement_computes_bounds_from_simple_object(self):
        class Identity:
            def __init__(self, key):
                self.key = key

        node = type(
            "Node",
            (),
            {
                "identity": Identity("NODE-1"),
                "x": 10.0,
                "y": 20.0,
                "z": 30.0,
                "width": 100.0,
                "depth": 200.0,
                "height": 300.0,
            },
        )()

        measurement = measure_scene_node_bounds(node)

        self.assertIsInstance(measurement, SceneNodeBoundsMeasurement)
        self.assertEqual(measurement.node_id, "NODE-1")
        self.assertEqual(measurement.x_min, 10.0)
        self.assertEqual(measurement.y_min, 20.0)
        self.assertEqual(measurement.z_min, 30.0)
        self.assertEqual(measurement.x_max, 110.0)
        self.assertEqual(measurement.y_max, 220.0)
        self.assertEqual(measurement.z_max, 330.0)

    def test_measurement_uses_id_fallback_when_identity_is_missing(self):
        node = type(
            "Node",
            (),
            {
                "id": "NODE-2",
                "x": 0.0,
                "y": 1.0,
                "z": 2.0,
                "width": 3.0,
                "depth": 4.0,
                "height": 5.0,
            },
        )()

        measurement = measure_scene_node_bounds(node)

        self.assertEqual(measurement.node_id, "NODE-2")
        self.assertEqual((measurement.x_min, measurement.y_min, measurement.z_min), (0.0, 1.0, 2.0))
        self.assertEqual((measurement.x_max, measurement.y_max, measurement.z_max), (3.0, 5.0, 7.0))

    def test_measurement_stores_source(self):
        node = type(
            "Node",
            (),
            {
                "id": "NODE-3",
                "x": 4.0,
                "y": 5.0,
                "z": 6.0,
                "width": 7.0,
                "depth": 8.0,
                "height": 9.0,
            },
        )()

        measurement = measure_scene_node_bounds(node, source="scene-graph")

        self.assertEqual(measurement.source, "scene-graph")

    def test_dataclass_fields_are_exact(self):
        self.assertTrue(is_dataclass(SceneNodeBoundsMeasurement))
        self.assertEqual(
            [field.name for field in fields(SceneNodeBoundsMeasurement)],
            [
                "node_id",
                "x_min",
                "y_min",
                "z_min",
                "x_max",
                "y_max",
                "z_max",
                "source",
            ],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.scene_node_bounds_measurement"
        )
        source = inspect.getsource(module)
        self.assertIn("measure_scene_node_bounds", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.scene_node_bounds_measurement"
        )
        source = inspect.getsource(module)

        for token in (
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "FreeCAD",
            "SpatialQueryEngine",
            "BoundingBox",
            "domain.builders.SceneNode",
            "domain.entities.SceneNode",
            "project_engineering.operational_",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_function_is_generic_and_component_agnostic(self):
        signature = inspect.signature(measure_scene_node_bounds)
        self.assertEqual(list(signature.parameters), ["node", "source"])
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)

    def test_does_not_import_boundingbox_or_spatialqueryengine_or_legacy_scene_nodes(self):
        module = importlib.import_module(
            "project_engineering.scene_node_bounds_measurement"
        )
        source = inspect.getsource(module)

        self.assertNotIn("from domain.topology import BoundingBox", source)
        self.assertNotIn("SpatialQueryEngine", source)
        self.assertNotIn("domain.builders.SceneNode", source)
        self.assertNotIn("domain.entities.SceneNode", source)


if __name__ == "__main__":
    unittest.main()
