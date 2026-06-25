import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestMotionCollisionFact(unittest.TestCase):
    def test_stores_moving_and_obstacle_component_ids(self):
        from project_engineering.motion_collision_fact import MotionCollisionFact

        fact = MotionCollisionFact(
            moving_component_id="MOV-1",
            obstacle_component_id="OBS-1",
        )

        self.assertEqual(fact.moving_component_id, "MOV-1")
        self.assertEqual(fact.obstacle_component_id, "OBS-1")

    def test_defaults_collision_type_to_empty_string(self):
        from project_engineering.motion_collision_fact import MotionCollisionFact

        fact = MotionCollisionFact(
            moving_component_id="MOV-2",
            obstacle_component_id="OBS-2",
        )

        self.assertEqual(fact.collision_type, "")

    def test_defaults_severity_to_error(self):
        from project_engineering.motion_collision_fact import MotionCollisionFact

        fact = MotionCollisionFact(
            moving_component_id="MOV-3",
            obstacle_component_id="OBS-3",
        )

        self.assertEqual(fact.severity, "error")

    def test_defaults_message_and_source_to_empty_strings(self):
        from project_engineering.motion_collision_fact import MotionCollisionFact

        fact = MotionCollisionFact(
            moving_component_id="MOV-4",
            obstacle_component_id="OBS-4",
        )

        self.assertEqual(fact.message, "")
        self.assertEqual(fact.source, "")

    def test_can_store_metadata_fields(self):
        from project_engineering.motion_collision_fact import MotionCollisionFact

        fact = MotionCollisionFact(
            moving_component_id="MOV-5",
            obstacle_component_id="OBS-5",
            collision_type="aabb_overlap",
            severity="warning",
            message="collision detected",
            source="motion-analysis",
        )

        self.assertEqual(fact.collision_type, "aabb_overlap")
        self.assertEqual(fact.severity, "warning")
        self.assertEqual(fact.message, "collision detected")
        self.assertEqual(fact.source, "motion-analysis")

    def test_dataclass_fields_are_exact(self):
        from project_engineering.motion_collision_fact import MotionCollisionFact

        self.assertTrue(is_dataclass(MotionCollisionFact))
        self.assertEqual(
            [field.name for field in fields(MotionCollisionFact)],
            [
                "moving_component_id",
                "obstacle_component_id",
                "collision_type",
                "severity",
                "message",
                "source",
            ],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.motion_collision_fact")
        source = inspect.getsource(module)

        self.assertIn("MotionCollisionFact", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.motion_collision_fact")
        source = inspect.getsource(module)

        for token in (
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
            "MotionEnvelopeFact",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_does_not_require_component_specific_fields(self):
        from project_engineering.motion_collision_fact import MotionCollisionFact

        signature = inspect.signature(MotionCollisionFact)
        self.assertEqual(
            list(signature.parameters),
            [
                "moving_component_id",
                "obstacle_component_id",
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
