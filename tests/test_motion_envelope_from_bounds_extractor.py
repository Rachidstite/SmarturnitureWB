import importlib
import inspect
import re
import unittest

from project_engineering.motion_envelope_fact import MotionEnvelopeFact
from project_engineering.motion_envelope_from_bounds_extractor import (
    extract_motion_envelope_from_bounds,
)
from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
)


class TestMotionEnvelopeFromBoundsExtractor(unittest.TestCase):
    def test_returns_motion_envelope_fact(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-1",
            x_min=1.0,
            y_min=2.0,
            z_min=3.0,
            x_max=4.0,
            y_max=5.0,
            z_max=6.0,
        )

        fact = extract_motion_envelope_from_bounds(bounds)

        self.assertIsInstance(fact, MotionEnvelopeFact)

    def test_uses_bounds_node_id_as_component_id(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-2",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=20.0,
            z_max=30.0,
        )

        fact = extract_motion_envelope_from_bounds(bounds)

        self.assertEqual(fact.component_id, "NODE-2")

    def test_copies_all_min_max_values(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-3",
            x_min=1.5,
            y_min=2.5,
            z_min=3.5,
            x_max=4.5,
            y_max=5.5,
            z_max=6.5,
        )

        fact = extract_motion_envelope_from_bounds(bounds)

        self.assertEqual((fact.x_min, fact.y_min, fact.z_min), (1.5, 2.5, 3.5))
        self.assertEqual((fact.x_max, fact.y_max, fact.z_max), (4.5, 5.5, 6.5))

    def test_preserves_motion_type_direction_and_source(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-4",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=1.0,
            y_max=1.0,
            z_max=1.0,
        )

        fact = extract_motion_envelope_from_bounds(
            bounds,
            motion_type="swing",
            direction="front",
            source="motion-extraction",
        )

        self.assertEqual(fact.motion_type, "swing")
        self.assertEqual(fact.direction, "front")
        self.assertEqual(fact.source, "motion-extraction")

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.motion_envelope_from_bounds_extractor"
        )
        source = inspect.getsource(module)

        for token in (
            "motion_engine",
            "collision",
            "rule",
            "decision",
            "FreeCAD",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "project_geometry",
            "scene_graph",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_does_not_require_component_specific_fields(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-5",
            x_min=10.0,
            y_min=20.0,
            z_min=30.0,
            x_max=40.0,
            y_max=50.0,
            z_max=60.0,
        )

        fact = extract_motion_envelope_from_bounds(bounds)

        self.assertEqual(fact.component_id, "NODE-5")
        self.assertFalse(hasattr(fact, "door"))
        self.assertFalse(hasattr(fact, "drawer"))
        self.assertFalse(hasattr(fact, "hinge"))
        self.assertFalse(hasattr(fact, "slide"))
        self.assertFalse(hasattr(fact, "shelf"))
        self.assertFalse(hasattr(fact, "panel"))

    def test_function_signature_is_generic(self):
        signature = inspect.signature(extract_motion_envelope_from_bounds)
        self.assertEqual(
            list(signature.parameters),
            ["bounds", "motion_type", "direction", "source"],
        )


if __name__ == "__main__":
    unittest.main()
