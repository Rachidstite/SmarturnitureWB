import importlib
import inspect
import re
import unittest

from project_engineering.installation_area_fact import InstallationAreaFact
from project_engineering.installation_fit_rule import evaluate_installation_fit
from project_engineering.operational_rule_result import OperationalRuleResult
from project_engineering.project_footprint import ProjectFootprint


class TestInstallationFitRule(unittest.TestCase):
    def test_perfect_fit_passes(self):
        footprint = ProjectFootprint(
            x_min=1.0,
            y_min=2.0,
            x_max=3.0,
            y_max=4.0,
        )
        area = InstallationAreaFact(
            area_id="AREA-1",
            x_min=1.0,
            y_min=2.0,
            x_max=3.0,
            y_max=4.0,
        )

        result = evaluate_installation_fit(footprint, area)

        self.assertIsInstance(result, OperationalRuleResult)
        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_smaller_footprint_passes(self):
        footprint = ProjectFootprint(
            x_min=2.0,
            y_min=3.0,
            x_max=8.0,
            y_max=9.0,
        )
        area = InstallationAreaFact(
            area_id="AREA-2",
            x_min=1.0,
            y_min=2.0,
            x_max=10.0,
            y_max=12.0,
        )

        result = evaluate_installation_fit(footprint, area)

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_left_overflow_fails(self):
        footprint = ProjectFootprint(
            x_min=0.0,
            y_min=2.0,
            x_max=5.0,
            y_max=6.0,
        )
        area = InstallationAreaFact(
            area_id="AREA-3",
            x_min=1.0,
            y_min=2.0,
            x_max=10.0,
            y_max=12.0,
        )

        result = evaluate_installation_fit(footprint, area)

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")

    def test_right_overflow_fails(self):
        footprint = ProjectFootprint(
            x_min=1.0,
            y_min=2.0,
            x_max=11.0,
            y_max=6.0,
        )
        area = InstallationAreaFact(
            area_id="AREA-4",
            x_min=1.0,
            y_min=2.0,
            x_max=10.0,
            y_max=12.0,
        )

        result = evaluate_installation_fit(footprint, area)

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")

    def test_top_overflow_fails(self):
        footprint = ProjectFootprint(
            x_min=1.0,
            y_min=2.0,
            x_max=6.0,
            y_max=13.0,
        )
        area = InstallationAreaFact(
            area_id="AREA-5",
            x_min=1.0,
            y_min=2.0,
            x_max=10.0,
            y_max=12.0,
        )

        result = evaluate_installation_fit(footprint, area)

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")

    def test_bottom_overflow_fails(self):
        footprint = ProjectFootprint(
            x_min=1.0,
            y_min=1.0,
            x_max=6.0,
            y_max=6.0,
        )
        area = InstallationAreaFact(
            area_id="AREA-6",
            x_min=1.0,
            y_min=2.0,
            x_max=10.0,
            y_max=12.0,
        )

        result = evaluate_installation_fit(footprint, area)

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")

    def test_result_capability_is_installation_fit(self):
        footprint = ProjectFootprint(
            x_min=1.0,
            y_min=2.0,
            x_max=3.0,
            y_max=4.0,
        )
        area = InstallationAreaFact(
            area_id="AREA-7",
            x_min=0.0,
            y_min=0.0,
            x_max=10.0,
            y_max=10.0,
        )

        result = evaluate_installation_fit(footprint, area)

        self.assertEqual(result.capability, "installation_fit")

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.installation_fit_rule")
        source = inspect.getsource(module)

        self.assertIn("evaluate_installation_fit", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.installation_fit_rule")
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
            "RoomEngine",
            "InstallationEngine",
            "CollisionEngine",
            "builder",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_function_signature_remains_generic(self):
        signature = inspect.signature(evaluate_installation_fit)
        self.assertEqual(
            list(signature.parameters),
            ["footprint", "installation_area"],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)

    def test_does_not_contain_banned_geometry_or_engine_logic(self):
        module = importlib.import_module("project_engineering.installation_fit_rule")
        source = inspect.getsource(module)
        source_lower = source.lower()

        for token in (
            "project_envelope",
            "collision",
            "adjacency",
            "alignment",
            "layout",
            "room",
            "installation engine",
            "installationengine",
            "collision engine",
            "scenegraph",
            "manufacturing",
            "cost",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source_lower)

        self.assertNotRegex(source, re.compile(r"\bclass\s+"))


if __name__ == "__main__":
    unittest.main()
