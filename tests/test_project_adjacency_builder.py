import importlib
import inspect
import re
import unittest

from project_engineering.project_adjacency_builder import build_project_adjacency_fact
from project_engineering.project_adjacency_fact import ProjectAdjacencyFact
from project_engineering.scene_node_bounds_measurement import SceneNodeBoundsMeasurement


class TestProjectAdjacencyBuilder(unittest.TestCase):
    def test_detects_x_axis_adjacency_first_to_second(self):
        first = SceneNodeBoundsMeasurement(
            node_id="NODE-A",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=10.0,
            z_max=10.0,
        )
        second = SceneNodeBoundsMeasurement(
            node_id="NODE-B",
            x_min=10.0,
            y_min=2.0,
            z_min=0.0,
            x_max=20.0,
            y_max=8.0,
            z_max=10.0,
        )

        fact = build_project_adjacency_fact(first, second)

        self.assertIsInstance(fact, ProjectAdjacencyFact)
        self.assertEqual(fact.relation, "adjacent")
        self.assertEqual(fact.axis, "x")
        self.assertEqual(fact.distance_mm, 0.0)

    def test_detects_x_axis_adjacency_second_to_first(self):
        first = SceneNodeBoundsMeasurement(
            node_id="NODE-A2",
            x_min=10.0,
            y_min=0.0,
            z_min=0.0,
            x_max=20.0,
            y_max=10.0,
            z_max=10.0,
        )
        second = SceneNodeBoundsMeasurement(
            node_id="NODE-B2",
            x_min=0.0,
            y_min=2.0,
            z_min=0.0,
            x_max=10.0,
            y_max=8.0,
            z_max=10.0,
        )

        fact = build_project_adjacency_fact(first, second)

        self.assertEqual(fact.relation, "adjacent")
        self.assertEqual(fact.axis, "x")
        self.assertEqual(fact.distance_mm, 0.0)

    def test_detects_y_axis_adjacency_first_to_second(self):
        first = SceneNodeBoundsMeasurement(
            node_id="NODE-A3",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=10.0,
            z_max=10.0,
        )
        second = SceneNodeBoundsMeasurement(
            node_id="NODE-B3",
            x_min=2.0,
            y_min=10.0,
            z_min=0.0,
            x_max=8.0,
            y_max=20.0,
            z_max=10.0,
        )

        fact = build_project_adjacency_fact(first, second)

        self.assertEqual(fact.relation, "adjacent")
        self.assertEqual(fact.axis, "y")
        self.assertEqual(fact.distance_mm, 0.0)

    def test_detects_y_axis_adjacency_second_to_first(self):
        first = SceneNodeBoundsMeasurement(
            node_id="NODE-A4",
            x_min=0.0,
            y_min=10.0,
            z_min=0.0,
            x_max=10.0,
            y_max=20.0,
            z_max=10.0,
        )
        second = SceneNodeBoundsMeasurement(
            node_id="NODE-B4",
            x_min=2.0,
            y_min=0.0,
            z_min=0.0,
            x_max=8.0,
            y_max=10.0,
            z_max=10.0,
        )

        fact = build_project_adjacency_fact(first, second)

        self.assertEqual(fact.relation, "adjacent")
        self.assertEqual(fact.axis, "y")
        self.assertEqual(fact.distance_mm, 0.0)

    def test_uses_tolerance_mm(self):
        first = SceneNodeBoundsMeasurement(
            node_id="NODE-T1",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=10.0,
            z_max=10.0,
        )
        second = SceneNodeBoundsMeasurement(
            node_id="NODE-T2",
            x_min=10.4,
            y_min=1.0,
            z_min=0.0,
            x_max=20.0,
            y_max=9.0,
            z_max=10.0,
        )

        fact = build_project_adjacency_fact(first, second, tolerance_mm=0.5)

        self.assertEqual(fact.relation, "adjacent")
        self.assertEqual(fact.axis, "x")
        self.assertAlmostEqual(fact.distance_mm, 0.4)

    def test_separate_components_return_separate_relation(self):
        first = SceneNodeBoundsMeasurement(
            node_id="NODE-S1",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=10.0,
            z_max=10.0,
        )
        second = SceneNodeBoundsMeasurement(
            node_id="NODE-S2",
            x_min=20.0,
            y_min=30.0,
            z_min=0.0,
            x_max=30.0,
            y_max=40.0,
            z_max=10.0,
        )

        fact = build_project_adjacency_fact(first, second)

        self.assertEqual(fact.relation, "separate")
        self.assertEqual(fact.axis, "")
        self.assertGreater(fact.distance_mm, 0.0)

    def test_stores_first_and_second_node_ids(self):
        first = SceneNodeBoundsMeasurement(
            node_id="NODE-ID-1",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=10.0,
            z_max=10.0,
        )
        second = SceneNodeBoundsMeasurement(
            node_id="NODE-ID-2",
            x_min=12.0,
            y_min=0.0,
            z_min=0.0,
            x_max=22.0,
            y_max=10.0,
            z_max=10.0,
        )

        fact = build_project_adjacency_fact(first, second)

        self.assertEqual(fact.first_component_id, "NODE-ID-1")
        self.assertEqual(fact.second_component_id, "NODE-ID-2")

    def test_sets_source_to_project_adjacency_builder(self):
        first = SceneNodeBoundsMeasurement(
            node_id="NODE-SRC-1",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=10.0,
            z_max=10.0,
        )
        second = SceneNodeBoundsMeasurement(
            node_id="NODE-SRC-2",
            x_min=15.0,
            y_min=0.0,
            z_min=0.0,
            x_max=25.0,
            y_max=10.0,
            z_max=10.0,
        )

        fact = build_project_adjacency_fact(first, second)

        self.assertEqual(fact.source, "project-adjacency-builder")

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.project_adjacency_builder")
        source = inspect.getsource(module)

        self.assertIn("build_project_adjacency_fact", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.project_adjacency_builder")
        source = inspect.getsource(module)

        for token in (
            "ProjectEnvelope",
            "ProjectFootprint",
            "FurnitureProject",
            "CabinetPlacement",
            "SceneGraph",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "FreeCAD",
            "collision",
            "alignment",
            "decision",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_function_signature_remains_generic(self):
        signature = inspect.signature(build_project_adjacency_fact)
        self.assertEqual(
            list(signature.parameters),
            ["first", "second", "tolerance_mm"],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)


if __name__ == "__main__":
    unittest.main()
