import importlib
import inspect
import re
import unittest
from unittest.mock import patch

from project_engineering.project_adjacency_aggregator import (
    aggregate_project_adjacency_facts,
)
from project_engineering.project_adjacency_fact import ProjectAdjacencyFact
from project_engineering.scene_node_bounds_measurement import SceneNodeBoundsMeasurement


class TestProjectAdjacencyAggregator(unittest.TestCase):
    def test_empty_list_returns_empty_list(self):
        self.assertEqual(aggregate_project_adjacency_facts([]), [])

    def test_single_item_returns_empty_list(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-1",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=10.0,
            z_max=10.0,
        )

        self.assertEqual(aggregate_project_adjacency_facts([bounds]), [])

    def test_two_items_returns_one_fact(self):
        bounds = [
            SceneNodeBoundsMeasurement(
                node_id="NODE-1",
                x_min=0.0,
                y_min=0.0,
                z_min=0.0,
                x_max=10.0,
                y_max=10.0,
                z_max=10.0,
            ),
            SceneNodeBoundsMeasurement(
                node_id="NODE-2",
                x_min=10.0,
                y_min=0.0,
                z_min=0.0,
                x_max=20.0,
                y_max=10.0,
                z_max=10.0,
            ),
        ]

        facts = aggregate_project_adjacency_facts(bounds)

        self.assertEqual(len(facts), 1)
        self.assertIsInstance(facts[0], ProjectAdjacencyFact)

    def test_three_items_returns_three_pair_facts(self):
        bounds = [
            SceneNodeBoundsMeasurement(
                node_id="NODE-1",
                x_min=0.0,
                y_min=0.0,
                z_min=0.0,
                x_max=10.0,
                y_max=10.0,
                z_max=10.0,
            ),
            SceneNodeBoundsMeasurement(
                node_id="NODE-2",
                x_min=10.0,
                y_min=0.0,
                z_min=0.0,
                x_max=20.0,
                y_max=10.0,
                z_max=10.0,
            ),
            SceneNodeBoundsMeasurement(
                node_id="NODE-3",
                x_min=20.0,
                y_min=0.0,
                z_min=0.0,
                x_max=30.0,
                y_max=10.0,
                z_max=10.0,
            ),
        ]

        facts = aggregate_project_adjacency_facts(bounds)

        self.assertEqual(len(facts), 3)

    def test_preserves_input_pair_order(self):
        bounds = [
            SceneNodeBoundsMeasurement(
                node_id="NODE-A",
                x_min=0.0,
                y_min=0.0,
                z_min=0.0,
                x_max=10.0,
                y_max=10.0,
                z_max=10.0,
            ),
            SceneNodeBoundsMeasurement(
                node_id="NODE-B",
                x_min=10.0,
                y_min=0.0,
                z_min=0.0,
                x_max=20.0,
                y_max=10.0,
                z_max=10.0,
            ),
            SceneNodeBoundsMeasurement(
                node_id="NODE-C",
                x_min=20.0,
                y_min=0.0,
                z_min=0.0,
                x_max=30.0,
                y_max=10.0,
                z_max=10.0,
            ),
        ]

        facts = aggregate_project_adjacency_facts(bounds)

        self.assertEqual(
            [(fact.first_component_id, fact.second_component_id) for fact in facts],
            [
                ("NODE-A", "NODE-B"),
                ("NODE-A", "NODE-C"),
                ("NODE-B", "NODE-C"),
            ],
        )

    def test_passes_tolerance_mm_to_build_project_adjacency_fact(self):
        module = importlib.import_module("project_engineering.project_adjacency_aggregator")

        bounds = [
            SceneNodeBoundsMeasurement(
                node_id="NODE-T1",
                x_min=0.0,
                y_min=0.0,
                z_min=0.0,
                x_max=10.0,
                y_max=10.0,
                z_max=10.0,
            ),
            SceneNodeBoundsMeasurement(
                node_id="NODE-T2",
                x_min=11.0,
                y_min=0.0,
                z_min=0.0,
                x_max=21.0,
                y_max=10.0,
                z_max=10.0,
            ),
        ]

        with patch.object(module, "build_project_adjacency_fact") as build_mock:
            build_mock.return_value = ProjectAdjacencyFact(
                first_component_id="NODE-T1",
                second_component_id="NODE-T2",
                relation="adjacent",
                axis="x",
                distance_mm=1.0,
                source="project-adjacency-builder",
            )
            aggregate_project_adjacency_facts(bounds, tolerance_mm=0.75)

        build_mock.assert_called_once_with(bounds[0], bounds[1], tolerance_mm=0.75)

    def test_does_not_filter_separate_facts(self):
        bounds = [
            SceneNodeBoundsMeasurement(
                node_id="NODE-S1",
                x_min=0.0,
                y_min=0.0,
                z_min=0.0,
                x_max=10.0,
                y_max=10.0,
                z_max=10.0,
            ),
            SceneNodeBoundsMeasurement(
                node_id="NODE-S2",
                x_min=30.0,
                y_min=30.0,
                z_min=0.0,
                x_max=40.0,
                y_max=40.0,
                z_max=10.0,
            ),
        ]

        facts = aggregate_project_adjacency_facts(bounds)

        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0].relation, "separate")

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.project_adjacency_aggregator")
        source = inspect.getsource(module)

        self.assertIn("aggregate_project_adjacency_facts", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.project_adjacency_aggregator")
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
        signature = inspect.signature(aggregate_project_adjacency_facts)
        self.assertEqual(
            list(signature.parameters),
            ["bounds_measurements", "tolerance_mm"],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)


if __name__ == "__main__":
    unittest.main()
