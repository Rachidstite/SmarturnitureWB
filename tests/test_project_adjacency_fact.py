import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestProjectAdjacencyFact(unittest.TestCase):
    def test_stores_first_and_second_component_ids(self):
        from project_engineering.project_adjacency_fact import ProjectAdjacencyFact

        fact = ProjectAdjacencyFact(
            first_component_id="COMP-1",
            second_component_id="COMP-2",
        )

        self.assertEqual(fact.first_component_id, "COMP-1")
        self.assertEqual(fact.second_component_id, "COMP-2")

    def test_defaults_relation_axis_and_source_to_empty_strings(self):
        from project_engineering.project_adjacency_fact import ProjectAdjacencyFact

        fact = ProjectAdjacencyFact(
            first_component_id="COMP-3",
            second_component_id="COMP-4",
        )

        self.assertEqual(fact.relation, "")
        self.assertEqual(fact.axis, "")
        self.assertEqual(fact.source, "")

    def test_defaults_distance_mm_to_zero(self):
        from project_engineering.project_adjacency_fact import ProjectAdjacencyFact

        fact = ProjectAdjacencyFact(
            first_component_id="COMP-5",
            second_component_id="COMP-6",
        )

        self.assertEqual(fact.distance_mm, 0.0)

    def test_can_store_relation_axis_distance_and_source(self):
        from project_engineering.project_adjacency_fact import ProjectAdjacencyFact

        fact = ProjectAdjacencyFact(
            first_component_id="COMP-7",
            second_component_id="COMP-8",
            relation="adjacent",
            axis="x",
            distance_mm=12.5,
            source="adjacency-analysis",
        )

        self.assertEqual(fact.relation, "adjacent")
        self.assertEqual(fact.axis, "x")
        self.assertEqual(fact.distance_mm, 12.5)
        self.assertEqual(fact.source, "adjacency-analysis")

    def test_dataclass_fields_are_exact(self):
        from project_engineering.project_adjacency_fact import ProjectAdjacencyFact

        self.assertTrue(is_dataclass(ProjectAdjacencyFact))
        self.assertEqual(
            [field.name for field in fields(ProjectAdjacencyFact)],
            [
                "first_component_id",
                "second_component_id",
                "relation",
                "axis",
                "distance_mm",
                "source",
            ],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.project_adjacency_fact")
        source = inspect.getsource(module)

        self.assertIn("ProjectAdjacencyFact", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.project_adjacency_fact")
        source = inspect.getsource(module)

        for token in (
            "extractor",
            "rule",
            "decision",
            "collision",
            "layout",
            "FurnitureProject",
            "CabinetPlacement",
            "SceneGraph",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "FreeCAD",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_does_not_require_component_specific_fields(self):
        from project_engineering.project_adjacency_fact import ProjectAdjacencyFact

        signature = inspect.signature(ProjectAdjacencyFact)
        self.assertEqual(
            list(signature.parameters),
            [
                "first_component_id",
                "second_component_id",
                "relation",
                "axis",
                "distance_mm",
                "source",
            ],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)


if __name__ == "__main__":
    unittest.main()
