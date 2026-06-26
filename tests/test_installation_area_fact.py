import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestInstallationAreaFact(unittest.TestCase):
    def test_stores_area_id_and_xy_bounds(self):
        from project_engineering.installation_area_fact import InstallationAreaFact

        fact = InstallationAreaFact(
            area_id="AREA-1",
            x_min=1.0,
            y_min=2.0,
            x_max=3.0,
            y_max=4.0,
        )

        self.assertEqual(fact.area_id, "AREA-1")
        self.assertEqual((fact.x_min, fact.y_min), (1.0, 2.0))
        self.assertEqual((fact.x_max, fact.y_max), (3.0, 4.0))

    def test_defaults_source_to_empty_string(self):
        from project_engineering.installation_area_fact import InstallationAreaFact

        fact = InstallationAreaFact(
            area_id="AREA-2",
            x_min=0.0,
            y_min=0.0,
            x_max=10.0,
            y_max=20.0,
        )

        self.assertEqual(fact.source, "")

    def test_can_store_source(self):
        from project_engineering.installation_area_fact import InstallationAreaFact

        fact = InstallationAreaFact(
            area_id="AREA-3",
            x_min=-1.0,
            y_min=-2.0,
            x_max=3.0,
            y_max=4.0,
            source="installation-area",
        )

        self.assertEqual(fact.source, "installation-area")

    def test_dataclass_fields_are_exact(self):
        from project_engineering.installation_area_fact import InstallationAreaFact

        self.assertTrue(is_dataclass(InstallationAreaFact))
        self.assertEqual(
            [field.name for field in fields(InstallationAreaFact)],
            ["area_id", "x_min", "y_min", "x_max", "y_max", "source"],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.installation_area_fact")
        source = inspect.getsource(module)

        self.assertIn("InstallationAreaFact", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.installation_area_fact")
        source = inspect.getsource(module)

        for token in (
            "ProjectFootprint",
            "ProjectEnvelope",
            "SceneGraph",
            "layout",
            "room",
            "installation engine",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "FreeCAD",
            "collision",
            "adjacency",
            "alignment",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertEqual(source.count("import"), 1)
        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_does_not_contain_project_footprint_or_geometry_logic(self):
        module = importlib.import_module("project_engineering.installation_area_fact")
        source = inspect.getsource(module)

        for token in (
            "project_footprint",
            "footprint",
            "collision",
            "adjacency",
            "alignment",
            "calculate",
            "compute",
            "derive",
            "resolve",
            "layout",
            "room",
            "installation",
            "engine",
            "SceneGraph",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertNotRegex(source, re.compile(r"\bdef\s+"))


if __name__ == "__main__":
    unittest.main()
