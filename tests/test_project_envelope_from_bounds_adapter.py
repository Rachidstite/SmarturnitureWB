import importlib
import inspect
import re
import unittest

from project_engineering.project_envelope import ProjectEnvelope
from project_engineering.project_envelope_from_bounds_adapter import (
    build_project_envelope_from_bounds,
)
from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
)


class TestProjectEnvelopeFromBoundsAdapter(unittest.TestCase):
    def test_builds_project_envelope_from_scene_node_bounds_measurement(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-1",
            x_min=1.0,
            y_min=2.0,
            z_min=3.0,
            x_max=4.0,
            y_max=5.0,
            z_max=6.0,
        )

        envelope = build_project_envelope_from_bounds(bounds)

        self.assertIsInstance(envelope, ProjectEnvelope)

    def test_copies_all_min_max_values(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-2",
            x_min=-10.0,
            y_min=-20.0,
            z_min=-30.0,
            x_max=40.0,
            y_max=50.0,
            z_max=60.0,
        )

        envelope = build_project_envelope_from_bounds(bounds)

        self.assertEqual((envelope.x_min, envelope.y_min, envelope.z_min), (-10.0, -20.0, -30.0))
        self.assertEqual((envelope.x_max, envelope.y_max, envelope.z_max), (40.0, 50.0, 60.0))

    def test_sets_source_to_project_envelope_from_bounds(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-3",
            x_min=0.0,
            y_min=1.0,
            z_min=2.0,
            x_max=3.0,
            y_max=4.0,
            z_max=5.0,
        )

        envelope = build_project_envelope_from_bounds(bounds)

        self.assertEqual(envelope.source, "project-envelope-from-bounds")

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.project_envelope_from_bounds_adapter"
        )
        source = inspect.getsource(module)

        self.assertIn("build_project_envelope_from_bounds", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.project_envelope_from_bounds_adapter"
        )
        source = inspect.getsource(module)

        for token in (
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
            "footprint",
            "adjacency",
            "alignment",
            "installation",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_function_signature_remains_generic(self):
        signature = inspect.signature(build_project_envelope_from_bounds)
        self.assertEqual(list(signature.parameters), ["bounds"])
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)

    def test_does_not_contain_banned_logic(self):
        module = importlib.import_module(
            "project_engineering.project_envelope_from_bounds_adapter"
        )
        source = inspect.getsource(module)

        for token in (
            "collision",
            "footprint",
            "adjacency",
            "alignment",
            "installation",
            "layout",
            "room",
            "manufacturing",
            "cost",
            "exports",
            "CNC",
            "SceneGraph",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertNotRegex(source, re.compile(r"\bclass\s+"))


if __name__ == "__main__":
    unittest.main()
