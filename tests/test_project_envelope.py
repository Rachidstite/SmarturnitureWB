import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestProjectEnvelope(unittest.TestCase):
    def test_stores_all_min_max_values(self):
        from project_engineering.project_envelope import ProjectEnvelope

        envelope = ProjectEnvelope(
            x_min=1.0,
            y_min=2.0,
            z_min=3.0,
            x_max=4.0,
            y_max=5.0,
            z_max=6.0,
        )

        self.assertEqual(
            (envelope.x_min, envelope.y_min, envelope.z_min),
            (1.0, 2.0, 3.0),
        )
        self.assertEqual(
            (envelope.x_max, envelope.y_max, envelope.z_max),
            (4.0, 5.0, 6.0),
        )

    def test_defaults_source_to_empty_string(self):
        from project_engineering.project_envelope import ProjectEnvelope

        envelope = ProjectEnvelope(
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=0.0,
            y_max=0.0,
            z_max=0.0,
        )

        self.assertEqual(envelope.source, "")

    def test_can_store_source(self):
        from project_engineering.project_envelope import ProjectEnvelope

        envelope = ProjectEnvelope(
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=20.0,
            z_max=30.0,
            source="project-geometry",
        )

        self.assertEqual(envelope.source, "project-geometry")

    def test_dataclass_fields_are_exact(self):
        from project_engineering.project_envelope import ProjectEnvelope

        self.assertTrue(is_dataclass(ProjectEnvelope))
        self.assertEqual(
            [field.name for field in fields(ProjectEnvelope)],
            [
                "x_min",
                "y_min",
                "z_min",
                "x_max",
                "y_max",
                "z_max",
                "source",
            ],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.project_envelope")
        source = inspect.getsource(module)

        self.assertIn("ProjectEnvelope", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.project_envelope")
        source = inspect.getsource(module)

        for token in (
            "builder",
            "footprint",
            "collision",
            "adjacency",
            "alignment",
            "SceneGraph",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "FreeCAD",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertEqual(source.count("import"), 1)
        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_no_geometry_logic_is_present(self):
        module = importlib.import_module("project_engineering.project_envelope")
        source = inspect.getsource(module)

        for token in (
            "footprint",
            "collision",
            "adjacency",
            "alignment",
            "calculate",
            "compute",
            "derive",
            "resolve",
            "builder",
            "SceneGraph",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertNotRegex(source, re.compile(r"\bdef\s+"))


if __name__ == "__main__":
    unittest.main()
