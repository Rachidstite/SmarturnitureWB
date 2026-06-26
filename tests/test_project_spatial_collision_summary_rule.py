import importlib
import inspect
import re
import unittest

from project_engineering.operational_rule_result import OperationalRuleResult
from project_engineering.project_spatial_summary_report import (
    ProjectSpatialSummaryReport,
)


class TestProjectSpatialCollisionSummaryRule(unittest.TestCase):
    def test_passes_when_has_collisions_is_false(self):
        from project_engineering.project_spatial_collision_summary_rule import (
            evaluate_project_spatial_collision_summary,
        )

        result = evaluate_project_spatial_collision_summary(
            ProjectSpatialSummaryReport(
                project_id="PROJECT-1",
                collision_count=0,
                has_collisions=False,
            )
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_fails_when_has_collisions_is_true(self):
        from project_engineering.project_spatial_collision_summary_rule import (
            evaluate_project_spatial_collision_summary,
        )

        result = evaluate_project_spatial_collision_summary(
            ProjectSpatialSummaryReport(
                project_id="PROJECT-2",
                collision_count=2,
                has_collisions=True,
            )
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")

    def test_failure_message_includes_project_id(self):
        from project_engineering.project_spatial_collision_summary_rule import (
            evaluate_project_spatial_collision_summary,
        )

        result = evaluate_project_spatial_collision_summary(
            ProjectSpatialSummaryReport(
                project_id="PROJECT-3",
                collision_count=4,
                has_collisions=True,
            )
        )

        self.assertIn("PROJECT-3", result.message)

    def test_failure_message_includes_collision_count(self):
        from project_engineering.project_spatial_collision_summary_rule import (
            evaluate_project_spatial_collision_summary,
        )

        result = evaluate_project_spatial_collision_summary(
            ProjectSpatialSummaryReport(
                project_id="PROJECT-4",
                collision_count=7,
                has_collisions=True,
            )
        )

        self.assertIn("collision_count=7", result.message)

    def test_uses_capability_project_spatial_collision(self):
        from project_engineering.project_spatial_collision_summary_rule import (
            evaluate_project_spatial_collision_summary,
        )

        result = evaluate_project_spatial_collision_summary(
            ProjectSpatialSummaryReport(
                project_id="PROJECT-5",
                collision_count=0,
                has_collisions=False,
            )
        )

        self.assertEqual(result.capability, "project_spatial_collision")

    def test_uses_component_id_from_report_project_id(self):
        from project_engineering.project_spatial_collision_summary_rule import (
            evaluate_project_spatial_collision_summary,
        )

        result = evaluate_project_spatial_collision_summary(
            ProjectSpatialSummaryReport(
                project_id="PROJECT-6",
                collision_count=1,
                has_collisions=True,
            )
        )

        self.assertEqual(result.component_id, "PROJECT-6")

    def test_sets_source_correctly(self):
        from project_engineering.project_spatial_collision_summary_rule import (
            evaluate_project_spatial_collision_summary,
        )

        result = evaluate_project_spatial_collision_summary(
            ProjectSpatialSummaryReport(
                project_id="PROJECT-7",
                collision_count=0,
                has_collisions=False,
            )
        )

        self.assertEqual(result.source, "project-spatial-collision-summary-rule")

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.project_spatial_collision_summary_rule"
        )
        source = inspect.getsource(module)

        self.assertIn("evaluate_project_spatial_collision_summary", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.project_spatial_collision_summary_rule"
        )
        source = inspect.getsource(module)

        for token in (
            "geometry",
            "collision calculation",
            "adjacency",
            "alignment",
            "builder",
            "aggregator",
            "decision",
            "Engine",
            "FurnitureProject",
            "CabinetPlacement",
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

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_function_signature_remains_generic(self):
        from project_engineering.project_spatial_collision_summary_rule import (
            evaluate_project_spatial_collision_summary,
        )

        signature = inspect.signature(evaluate_project_spatial_collision_summary)
        self.assertEqual(
            list(signature.parameters),
            [
                "report",
                "rule_id",
                "source",
            ],
        )
        self.assertNotIn("self", signature.parameters)
        self.assertNotIn("cls", signature.parameters)

    def test_does_not_contain_engine_terminology(self):
        module = importlib.import_module(
            "project_engineering.project_spatial_collision_summary_rule"
        )
        source = inspect.getsource(module)

        self.assertNotIn("Engine", source)
        self.assertIsNone(re.search(r"\bEngine\b", source))


if __name__ == "__main__":
    unittest.main()
