import importlib
import inspect
import re
import unittest

from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
)
from project_engineering.simple_door_swing_motion_envelope_extractor import (
    extract_simple_door_swing_motion_envelope,
)


class TestSimpleDoorSwingAabbContract(unittest.TestCase):
    def test_source_explicitly_shows_aabb_approximation_inputs(self):
        module = importlib.import_module(
            "project_engineering.simple_door_swing_motion_envelope_extractor"
        )
        source = inspect.getsource(module)

        self.assertIn("extract_simple_door_swing_motion_envelope", source)
        self.assertIn("swing_depth_mm", source)
        self.assertIn("MotionEnvelopeFact", source)

    def test_source_does_not_contain_arc_math_or_engine_terms(self):
        module = importlib.import_module(
            "project_engineering.simple_door_swing_motion_envelope_extractor"
        )
        source = inspect.getsource(module)

        for token in (
            "arc",
            "angle",
            "hinge_axis",
            "rotation",
            "sin",
            "cos",
            "radians",
            "DoorEngine",
            "DoorSwingEngine",
            "MotionSimulator",
            "FreeCAD",
            "scene_graph",
            "project_geometry",
            "manufacturing",
            "cost",
            "exports",
            "CNC",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_behavior_remains_aabb_only_front_direction(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="DOOR-AABB-1",
            x_min=1.0,
            y_min=2.0,
            z_min=3.0,
            x_max=4.0,
            y_max=5.0,
            z_max=6.0,
        )

        fact = extract_simple_door_swing_motion_envelope(
            bounds,
            swing_depth_mm=25.0,
            direction="front",
        )

        self.assertEqual(fact.x_min, 1.0)
        self.assertEqual(fact.x_max, 4.0)
        self.assertEqual(fact.z_min, 3.0)
        self.assertEqual(fact.z_max, 6.0)
        self.assertEqual(fact.y_min, 2.0)
        self.assertEqual(fact.y_max, 30.0)

    def test_behavior_remains_aabb_only_back_direction(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="DOOR-AABB-2",
            x_min=10.0,
            y_min=20.0,
            z_min=30.0,
            x_max=40.0,
            y_max=50.0,
            z_max=60.0,
        )

        fact = extract_simple_door_swing_motion_envelope(
            bounds,
            swing_depth_mm=15.0,
            direction="back",
        )

        self.assertEqual(fact.x_min, 10.0)
        self.assertEqual(fact.x_max, 40.0)
        self.assertEqual(fact.z_min, 30.0)
        self.assertEqual(fact.z_max, 60.0)
        self.assertEqual(fact.y_min, 5.0)
        self.assertEqual(fact.y_max, 50.0)


if __name__ == "__main__":
    unittest.main()
