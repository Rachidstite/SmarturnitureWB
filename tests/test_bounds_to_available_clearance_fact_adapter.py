import importlib
import inspect
import re
import unittest

from project_engineering.bounds_to_available_clearance_fact_adapter import (
    build_available_clearance_fact_from_bounds_measurement,
)
from project_engineering.available_operational_clearance_fact import (
    AvailableOperationalClearanceFact,
)
from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
)


class TestBoundsToAvailableClearanceFactAdapter(unittest.TestCase):
    def test_converts_bounds_node_id_to_fact_component_id(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-10",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=20.0,
            z_max=30.0,
        )

        fact = build_available_clearance_fact_from_bounds_measurement(
            bounds,
            available_clearance_mm=12.0,
        )

        self.assertIsInstance(fact, AvailableOperationalClearanceFact)
        self.assertEqual(fact.component_id, "NODE-10")

    def test_preserves_available_clearance_mm(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-11",
            x_min=1.0,
            y_min=2.0,
            z_min=3.0,
            x_max=4.0,
            y_max=5.0,
            z_max=6.0,
        )

        fact = build_available_clearance_fact_from_bounds_measurement(
            bounds,
            available_clearance_mm=7.5,
        )

        self.assertEqual(fact.available_clearance_mm, 7.5)

    def test_preserves_direction_and_source(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-12",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=1.0,
            y_max=1.0,
            z_max=1.0,
        )

        fact = build_available_clearance_fact_from_bounds_measurement(
            bounds,
            available_clearance_mm=5.0,
            direction="front",
            source="bounds-adapter",
        )

        self.assertEqual(fact.direction, "front")
        self.assertEqual(fact.source, "bounds-adapter")

    def test_function_signature_is_generic(self):
        signature = inspect.signature(
            build_available_clearance_fact_from_bounds_measurement
        )
        self.assertEqual(
            list(signature.parameters),
            ["bounds", "available_clearance_mm", "direction", "source"],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.bounds_to_available_clearance_fact_adapter"
        )
        source = inspect.getsource(module)

        for token in (
            "rules",
            "decision",
            "readiness",
            "SpatialQueryEngine",
            "BoundingBox",
            "FreeCAD",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "operational_clearance_facts_rule",
            "operational_clearance_distance_rule",
            "project_engineering.operational_",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_imports_only_allowed_types(self):
        module = importlib.import_module(
            "project_engineering.bounds_to_available_clearance_fact_adapter"
        )
        source = inspect.getsource(module)

        self.assertIn(
            "from project_engineering.available_operational_clearance_fact import",
            source,
        )
        self.assertIn(
            "from project_engineering.scene_node_bounds_measurement import",
            source,
        )

    def test_does_not_require_component_specific_fields(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-13",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=2.0,
            y_max=2.0,
            z_max=2.0,
        )

        fact = build_available_clearance_fact_from_bounds_measurement(
            bounds,
            available_clearance_mm=1.25,
        )

        self.assertEqual(fact.component_id, "NODE-13")
        self.assertFalse(hasattr(fact, "door"))
        self.assertFalse(hasattr(fact, "drawer"))
        self.assertFalse(hasattr(fact, "hinge"))
        self.assertFalse(hasattr(fact, "slide"))
        self.assertFalse(hasattr(fact, "shelf"))
        self.assertFalse(hasattr(fact, "panel"))


if __name__ == "__main__":
    unittest.main()
