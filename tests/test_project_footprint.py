import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestProjectFootprint(unittest.TestCase):
    def test_stores_xy_min_max_values(self):
        from project_engineering.project_footprint import ProjectFootprint

        footprint = ProjectFootprint(
            x_min=1.0,
            y_min=2.0,
            x_max=3.0,
            y_max=4.0,
        )

        self.assertEqual((footprint.x_min, footprint.y_min), (1.0, 2.0))
        self.assertEqual((footprint.x_max, footprint.y_max), (3.0, 4.0))

    def test_defaults_source_to_empty_string(self):
        from project_engineering.project_footprint import ProjectFootprint

        footprint = ProjectFootprint(
            x_min=0.0,
            y_min=0.0,
            x_max=0.0,
            y_max=0.0,
        )

        self.assertEqual(footprint.source, "")

    def test_can_store_source(self):
        from project_engineering.project_footprint import ProjectFootprint

        footprint = ProjectFootprint(
            x_min=-1.0,
            y_min=-2.0,
            x_max=3.0,
            y_max=4.0,
            source="project-footprint",
        )

        self.assertEqual(footprint.source, "project-footprint")

    def test_dataclass_fields_are_exact(self):
        from project_engineering.project_footprint import ProjectFootprint

        self.assertTrue(is_dataclass(ProjectFootprint))
        self.assertEqual(
            [field.name for field in fields(ProjectFootprint)],
            ["x_min", "y_min", "x_max", "y_max", "source"],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.project_footprint")
        source = inspect.getsource(module)

        self.assertIn("ProjectFootprint", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.project_footprint")
        source = inspect.getsource(module)

        for token in (
            "ProjectEnvelope",
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
            "builder",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertEqual(source.count("import"), 1)
        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_does_not_contain_envelope_or_geometry_logic(self):
        module = importlib.import_module("project_engineering.project_footprint")
        source = inspect.getsource(module)

        for token in (
            "envelope",
            "collision",
            "adjacency",
            "alignment",
            "calculate",
            "compute",
            "derive",
            "resolve",
            "build_",
            "SceneGraph",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertNotRegex(source, re.compile(r"\bdef\s+"))


if __name__ == "__main__":
    unittest.main()
