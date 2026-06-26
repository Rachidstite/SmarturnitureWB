import importlib
import inspect
import re
import unittest

from project_engineering.project_envelope import ProjectEnvelope
from project_engineering.project_envelope_builder import build_project_envelope


class TestProjectEnvelopeBuilder(unittest.TestCase):
    def test_single_envelope_returns_identical_values(self):
        envelope = ProjectEnvelope(
            x_min=1.0,
            y_min=2.0,
            z_min=3.0,
            x_max=4.0,
            y_max=5.0,
            z_max=6.0,
            source="input-source",
        )

        result = build_project_envelope([envelope])

        self.assertIsInstance(result, ProjectEnvelope)
        self.assertEqual(
            (result.x_min, result.y_min, result.z_min),
            (1.0, 2.0, 3.0),
        )
        self.assertEqual(
            (result.x_max, result.y_max, result.z_max),
            (4.0, 5.0, 6.0),
        )
        self.assertEqual(result.source, "project-envelope-builder")

    def test_multiple_envelopes_merge_correctly(self):
        result = build_project_envelope(
            [
                ProjectEnvelope(
                    x_min=10.0,
                    y_min=20.0,
                    z_min=30.0,
                    x_max=40.0,
                    y_max=50.0,
                    z_max=60.0,
                ),
                ProjectEnvelope(
                    x_min=5.0,
                    y_min=15.0,
                    z_min=25.0,
                    x_max=45.0,
                    y_max=55.0,
                    z_max=65.0,
                ),
                ProjectEnvelope(
                    x_min=7.0,
                    y_min=18.0,
                    z_min=22.0,
                    x_max=42.0,
                    y_max=58.0,
                    z_max=68.0,
                ),
            ]
        )

        self.assertEqual((result.x_min, result.y_min, result.z_min), (5.0, 15.0, 22.0))
        self.assertEqual((result.x_max, result.y_max, result.z_max), (45.0, 58.0, 68.0))
        self.assertEqual(result.source, "project-envelope-builder")

    def test_negative_coordinates_work(self):
        result = build_project_envelope(
            [
                ProjectEnvelope(
                    x_min=-10.0,
                    y_min=-20.0,
                    z_min=-30.0,
                    x_max=-5.0,
                    y_max=-15.0,
                    z_max=-25.0,
                ),
                ProjectEnvelope(
                    x_min=-12.0,
                    y_min=-18.0,
                    z_min=-35.0,
                    x_max=-3.0,
                    y_max=-10.0,
                    z_max=-20.0,
                ),
            ]
        )

        self.assertEqual((result.x_min, result.y_min, result.z_min), (-12.0, -20.0, -35.0))
        self.assertEqual((result.x_max, result.y_max, result.z_max), (-3.0, -10.0, -20.0))

    def test_empty_list_raises_value_error(self):
        with self.assertRaises(ValueError):
            build_project_envelope([])

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.project_envelope_builder")
        source = inspect.getsource(module)

        self.assertIn("build_project_envelope", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.project_envelope_builder")
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
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_function_signature_remains_generic(self):
        signature = inspect.signature(build_project_envelope)
        self.assertEqual(list(signature.parameters), ["envelopes"])

        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)

    def test_does_not_contain_geometry_logic_or_scenegraph_hooks(self):
        module = importlib.import_module("project_engineering.project_envelope_builder")
        source = inspect.getsource(module)

        for token in (
            "compute",
            "calculate",
            "derive",
            "resolve",
            "SceneGraph",
            "FurnitureProject",
            "CabinetPlacement",
            "collision",
            "footprint",
            "adjacency",
            "alignment",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertNotRegex(source, re.compile(r"\bclass\s+"))


if __name__ == "__main__":
    unittest.main()
