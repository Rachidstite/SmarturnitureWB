import importlib
import inspect
import re
import unittest

from project_engineering.motion_envelope_fact import MotionEnvelopeFact
from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
)
from project_engineering.simple_door_swing_motion_envelope_extractor import (
    extract_simple_door_swing_motion_envelope,
)


class TestSimpleDoorSwingMotionEnvelopeExtractor(unittest.TestCase):
    def test_front_swing_expands_y_max_by_swing_depth_mm(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="DOOR-1",
            x_min=0.0,
            y_min=100.0,
            z_min=0.0,
            x_max=20.0,
            y_max=120.0,
            z_max=200.0,
        )

        fact = extract_simple_door_swing_motion_envelope(
            bounds,
            swing_depth_mm=50.0,
            direction="front",
        )

        self.assertEqual(fact.y_min, 100.0)
        self.assertEqual(fact.y_max, 170.0)

    def test_back_swing_expands_y_min_backward_by_swing_depth_mm(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="DOOR-2",
            x_min=10.0,
            y_min=100.0,
            z_min=20.0,
            x_max=30.0,
            y_max=120.0,
            z_max=220.0,
        )

        fact = extract_simple_door_swing_motion_envelope(
            bounds,
            swing_depth_mm=40.0,
            direction="back",
        )

        self.assertEqual(fact.y_min, 60.0)
        self.assertEqual(fact.y_max, 120.0)

    def test_xz_extents_are_copied(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="DOOR-3",
            x_min=1.0,
            y_min=2.0,
            z_min=3.0,
            x_max=4.0,
            y_max=5.0,
            z_max=6.0,
        )

        fact = extract_simple_door_swing_motion_envelope(bounds, swing_depth_mm=25.0)

        self.assertEqual((fact.x_min, fact.x_max), (1.0, 4.0))
        self.assertEqual((fact.z_min, fact.z_max), (3.0, 6.0))

    def test_component_id_comes_from_closed_bounds_node_id(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="DOOR-4",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=1.0,
            y_max=1.0,
            z_max=1.0,
        )

        fact = extract_simple_door_swing_motion_envelope(bounds, swing_depth_mm=10.0)

        self.assertEqual(fact.component_id, "DOOR-4")

    def test_motion_type_is_door_swing(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="DOOR-5",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=1.0,
            y_max=1.0,
            z_max=1.0,
        )

        fact = extract_simple_door_swing_motion_envelope(bounds, swing_depth_mm=10.0)

        self.assertEqual(fact.motion_type, "door_swing")

    def test_direction_and_source_are_preserved(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="DOOR-6",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=1.0,
            y_max=1.0,
            z_max=1.0,
        )

        fact = extract_simple_door_swing_motion_envelope(
            bounds,
            swing_depth_mm=10.0,
            direction="front",
            source="door-motion",
        )

        self.assertEqual(fact.direction, "front")
        self.assertEqual(fact.source, "door-motion")

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.simple_door_swing_motion_envelope_extractor"
        )
        source = inspect.getsource(module)

        for token in (
            "DoorMotionEngine",
            "DoorSwingEngine",
            "MotionSimulator",
            "FreeCAD",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "scene_graph",
            "project_geometry",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_no_component_specific_engine_class(self):
        module = importlib.import_module(
            "project_engineering.simple_door_swing_motion_envelope_extractor"
        )
        source = inspect.getsource(module)

        self.assertNotIn("class DoorMotionEngine", source)
        self.assertNotIn("class DoorSwingEngine", source)
        self.assertNotIn("class MotionSimulator", source)

    def test_function_signature_is_generic(self):
        signature = inspect.signature(
            extract_simple_door_swing_motion_envelope
        )
        self.assertEqual(
            list(signature.parameters),
            ["closed_bounds", "swing_depth_mm", "direction", "source"],
        )


if __name__ == "__main__":
    unittest.main()
