import importlib
import inspect
import re
import unittest

from project_engineering.project_envelope import ProjectEnvelope
from project_engineering.project_footprint import ProjectFootprint
from project_engineering.project_footprint_builder import (
    build_project_footprint_from_envelope,
)


class TestProjectFootprintBuilder(unittest.TestCase):
    def test_builds_project_footprint_from_project_envelope(self):
        envelope = ProjectEnvelope(
            x_min=1.0,
            y_min=2.0,
            z_min=3.0,
            x_max=4.0,
            y_max=5.0,
            z_max=6.0,
        )

        footprint = build_project_footprint_from_envelope(envelope)

        self.assertIsInstance(footprint, ProjectFootprint)

    def test_copies_xy_bounds(self):
        envelope = ProjectEnvelope(
            x_min=-10.0,
            y_min=-20.0,
            z_min=30.0,
            x_max=40.0,
            y_max=50.0,
            z_max=60.0,
        )

        footprint = build_project_footprint_from_envelope(envelope)

        self.assertEqual((footprint.x_min, footprint.y_min), (-10.0, -20.0))
        self.assertEqual((footprint.x_max, footprint.y_max), (40.0, 50.0))

    def test_ignores_z_bounds_correctly(self):
        envelope = ProjectEnvelope(
            x_min=0.0,
            y_min=1.0,
            z_min=999.0,
            x_max=2.0,
            y_max=3.0,
            z_max=888.0,
        )

        footprint = build_project_footprint_from_envelope(envelope)

        self.assertEqual((footprint.x_min, footprint.y_min), (0.0, 1.0))
        self.assertEqual((footprint.x_max, footprint.y_max), (2.0, 3.0))
        self.assertEqual(footprint.source, "project-footprint-builder")

    def test_sets_source_to_project_footprint_builder(self):
        envelope = ProjectEnvelope(
            x_min=1.0,
            y_min=1.0,
            z_min=1.0,
            x_max=2.0,
            y_max=2.0,
            z_max=2.0,
        )

        footprint = build_project_footprint_from_envelope(envelope)

        self.assertEqual(footprint.source, "project-footprint-builder")

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.project_footprint_builder")
        source = inspect.getsource(module)

        self.assertIn("build_project_footprint_from_envelope", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.project_footprint_builder")
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
            "adjacency",
            "alignment",
            "installation",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_function_signature_remains_generic(self):
        signature = inspect.signature(build_project_footprint_from_envelope)
        self.assertEqual(list(signature.parameters), ["envelope"])
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)

    def test_does_not_contain_banned_logic(self):
        module = importlib.import_module("project_engineering.project_footprint_builder")
        source = inspect.getsource(module)

        for token in (
            "collision",
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
