import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestProjectCollisionFact(unittest.TestCase):
    def test_stores_first_and_second_component_ids(self):
        from project_engineering.project_collision_fact import ProjectCollisionFact

        fact = ProjectCollisionFact(
            first_component_id="COMP-1",
            second_component_id="COMP-2",
        )

        self.assertEqual(fact.first_component_id, "COMP-1")
        self.assertEqual(fact.second_component_id, "COMP-2")

    def test_defaults_collision_type_to_empty_string(self):
        from project_engineering.project_collision_fact import ProjectCollisionFact

        fact = ProjectCollisionFact(
            first_component_id="COMP-3",
            second_component_id="COMP-4",
        )

        self.assertEqual(fact.collision_type, "")

    def test_defaults_severity_to_error(self):
        from project_engineering.project_collision_fact import ProjectCollisionFact

        fact = ProjectCollisionFact(
            first_component_id="COMP-5",
            second_component_id="COMP-6",
        )

        self.assertEqual(fact.severity, "error")

    def test_defaults_message_and_source_to_empty_strings(self):
        from project_engineering.project_collision_fact import ProjectCollisionFact

        fact = ProjectCollisionFact(
            first_component_id="COMP-7",
            second_component_id="COMP-8",
        )

        self.assertEqual(fact.message, "")
        self.assertEqual(fact.source, "")

    def test_can_store_metadata_fields(self):
        from project_engineering.project_collision_fact import ProjectCollisionFact

        fact = ProjectCollisionFact(
            first_component_id="COMP-9",
            second_component_id="COMP-10",
            collision_type="static_overlap",
            severity="warning",
            message="collision detected",
            source="project-analysis",
        )

        self.assertEqual(fact.collision_type, "static_overlap")
        self.assertEqual(fact.severity, "warning")
        self.assertEqual(fact.message, "collision detected")
        self.assertEqual(fact.source, "project-analysis")

    def test_dataclass_fields_are_exact(self):
        from project_engineering.project_collision_fact import ProjectCollisionFact

        self.assertTrue(is_dataclass(ProjectCollisionFact))
        self.assertEqual(
            [field.name for field in fields(ProjectCollisionFact)],
            [
                "first_component_id",
                "second_component_id",
                "collision_type",
                "severity",
                "message",
                "source",
            ],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.project_collision_fact")
        source = inspect.getsource(module)

        self.assertIn("ProjectCollisionFact", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.project_collision_fact")
        source = inspect.getsource(module)

        for token in (
            "MotionCollisionFact",
            "MotionEngine",
            "CollisionEngine",
            "DoorEngine",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "scene_graph",
            "project_geometry",
            "OperationalRuleResult",
            "OperationalDecisionReport",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_does_not_require_component_specific_fields(self):
        from project_engineering.project_collision_fact import ProjectCollisionFact

        signature = inspect.signature(ProjectCollisionFact)
        self.assertEqual(
            list(signature.parameters),
            [
                "first_component_id",
                "second_component_id",
                "collision_type",
                "severity",
                "message",
                "source",
            ],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)


if __name__ == "__main__":
    unittest.main()
