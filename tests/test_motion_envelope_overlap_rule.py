import importlib
import inspect
import re
import unittest

from project_engineering.motion_envelope_fact import MotionEnvelopeFact
from project_engineering.motion_envelope_overlap_rule import (
    evaluate_motion_envelope_overlap,
)


class TestMotionEnvelopeOverlapRule(unittest.TestCase):
    def test_non_overlapping_envelopes_pass(self):
        moving = MotionEnvelopeFact(
            component_id="MOV-1",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=10.0,
            z_max=10.0,
        )
        obstacle = MotionEnvelopeFact(
            component_id="OBS-1",
            x_min=20.0,
            y_min=20.0,
            z_min=20.0,
            x_max=30.0,
            y_max=30.0,
            z_max=30.0,
        )

        result = evaluate_motion_envelope_overlap(moving, obstacle)

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_overlapping_envelopes_fail(self):
        moving = MotionEnvelopeFact(
            component_id="MOV-2",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=10.0,
            z_max=10.0,
        )
        obstacle = MotionEnvelopeFact(
            component_id="OBS-2",
            x_min=5.0,
            y_min=5.0,
            z_min=5.0,
            x_max=15.0,
            y_max=15.0,
            z_max=15.0,
        )

        result = evaluate_motion_envelope_overlap(moving, obstacle)

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("MOV-2", result.message)
        self.assertIn("OBS-2", result.message)

    def test_touching_edges_do_not_count_as_overlap(self):
        moving = MotionEnvelopeFact(
            component_id="MOV-3",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=10.0,
            z_max=10.0,
        )
        obstacle = MotionEnvelopeFact(
            component_id="OBS-3",
            x_min=10.0,
            y_min=10.0,
            z_min=10.0,
            x_max=20.0,
            y_max=20.0,
            z_max=20.0,
        )

        result = evaluate_motion_envelope_overlap(moving, obstacle)

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_result_uses_moving_envelope_component_id(self):
        moving = MotionEnvelopeFact(
            component_id="MOV-4",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=12.0,
            y_max=12.0,
            z_max=12.0,
        )
        obstacle = MotionEnvelopeFact(
            component_id="OBS-4",
            x_min=6.0,
            y_min=6.0,
            z_min=6.0,
            x_max=18.0,
            y_max=18.0,
            z_max=18.0,
        )

        result = evaluate_motion_envelope_overlap(moving, obstacle)

        self.assertEqual(result.component_id, "MOV-4")

    def test_result_capability_is_motion(self):
        moving = MotionEnvelopeFact(
            component_id="MOV-5",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=1.0,
            y_max=1.0,
            z_max=1.0,
        )
        obstacle = MotionEnvelopeFact(
            component_id="OBS-5",
            x_min=0.5,
            y_min=0.5,
            z_min=0.5,
            x_max=2.0,
            y_max=2.0,
            z_max=2.0,
        )

        result = evaluate_motion_envelope_overlap(moving, obstacle)

        self.assertEqual(result.capability, "motion")

    def test_failure_message_mentions_both_ids(self):
        moving = MotionEnvelopeFact(
            component_id="MOV-6",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=2.0,
            y_max=2.0,
            z_max=2.0,
        )
        obstacle = MotionEnvelopeFact(
            component_id="OBS-6",
            x_min=1.0,
            y_min=1.0,
            z_min=1.0,
            x_max=3.0,
            y_max=3.0,
            z_max=3.0,
        )

        result = evaluate_motion_envelope_overlap(moving, obstacle)

        self.assertIn("MOV-6", result.message)
        self.assertIn("OBS-6", result.message)

    def test_preserves_rule_id_and_source(self):
        moving = MotionEnvelopeFact(
            component_id="MOV-7",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=5.0,
            y_max=5.0,
            z_max=5.0,
        )
        obstacle = MotionEnvelopeFact(
            component_id="OBS-7",
            x_min=1.0,
            y_min=1.0,
            z_min=1.0,
            x_max=6.0,
            y_max=6.0,
            z_max=6.0,
        )

        result = evaluate_motion_envelope_overlap(
            moving,
            obstacle,
            rule_id="RULE-OVERLAP-01",
            source="motion-test",
        )

        self.assertEqual(result.rule_id, "RULE-OVERLAP-01")
        self.assertEqual(result.source, "motion-test")

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.motion_envelope_overlap_rule"
        )
        source = inspect.getsource(module)

        for token in (
            "motion_engine",
            "collision_engine",
            "simulation",
            "time-step",
            "FreeCAD",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "SceneGraph",
            "project_geometry",
            "DoorEngine",
            "DrawerEngine",
            "CollisionEngine",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_does_not_use_component_specific_terminology_in_source(self):
        module = importlib.import_module(
            "project_engineering.motion_envelope_overlap_rule"
        )
        source = inspect.getsource(module)

        self.assertNotIn("DoorEngine", source)
        self.assertNotIn("DrawerEngine", source)
        self.assertNotIn("CollisionEngine", source)


if __name__ == "__main__":
    unittest.main()
