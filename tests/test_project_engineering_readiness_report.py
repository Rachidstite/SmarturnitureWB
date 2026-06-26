import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestProjectEngineeringReadinessReport(unittest.TestCase):
    def test_defaults_project_id_and_source_to_empty_strings(self):
        from project_engineering.project_engineering_readiness_report import (
            ProjectEngineeringReadinessReport,
        )

        report = ProjectEngineeringReadinessReport()

        self.assertEqual(report.project_id, "")
        self.assertEqual(report.source, "")

    def test_defaults_readiness_booleans_to_false(self):
        from project_engineering.project_engineering_readiness_report import (
            ProjectEngineeringReadinessReport,
        )

        report = ProjectEngineeringReadinessReport()

        self.assertFalse(report.ready_for_engineering_release)
        self.assertFalse(report.ready_for_manufacturing_handoff)

    def test_defaults_counts_to_zero(self):
        from project_engineering.project_engineering_readiness_report import (
            ProjectEngineeringReadinessReport,
        )

        report = ProjectEngineeringReadinessReport()

        self.assertEqual(report.blocking_violation_count, 0)
        self.assertEqual(report.warning_count, 0)

    def test_can_store_all_fields(self):
        from project_engineering.project_engineering_readiness_report import (
            ProjectEngineeringReadinessReport,
        )

        report = ProjectEngineeringReadinessReport(
            project_id="PROJECT-1",
            ready_for_engineering_release=True,
            ready_for_manufacturing_handoff=True,
            blocking_violation_count=3,
            warning_count=1,
            source="engineering-readiness-builder",
        )

        self.assertEqual(report.project_id, "PROJECT-1")
        self.assertTrue(report.ready_for_engineering_release)
        self.assertTrue(report.ready_for_manufacturing_handoff)
        self.assertEqual(report.blocking_violation_count, 3)
        self.assertEqual(report.warning_count, 1)
        self.assertEqual(report.source, "engineering-readiness-builder")

    def test_dataclass_fields_are_exact(self):
        from project_engineering.project_engineering_readiness_report import (
            ProjectEngineeringReadinessReport,
        )

        self.assertTrue(is_dataclass(ProjectEngineeringReadinessReport))
        self.assertEqual(
            [field.name for field in fields(ProjectEngineeringReadinessReport)],
            [
                "project_id",
                "ready_for_engineering_release",
                "ready_for_manufacturing_handoff",
                "blocking_violation_count",
                "warning_count",
                "source",
            ],
        )

        signature = inspect.signature(ProjectEngineeringReadinessReport)
        self.assertEqual(
            list(signature.parameters),
            [
                "project_id",
                "ready_for_engineering_release",
                "ready_for_manufacturing_handoff",
                "blocking_violation_count",
                "warning_count",
                "source",
            ],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.project_engineering_readiness_report"
        )
        source = inspect.getsource(module)

        self.assertIn("ProjectEngineeringReadinessReport", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.project_engineering_readiness_report"
        )
        source = inspect.getsource(module)

        for token in (
            "builder",
            "rule",
            "decision",
            "manufacturing logic",
            "cost",
            "export",
            "CNC",
            "FurnitureProject",
            "CabinetPlacement",
            "SceneGraph",
            "FreeCAD",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_does_not_contain_logic_keywords(self):
        module = importlib.import_module(
            "project_engineering.project_engineering_readiness_report"
        )
        source = inspect.getsource(module)

        for token in (
            "builder",
            "rule",
            "decision",
            "cost",
            "export",
            "CNC",
            "if ",
            "for ",
            "while ",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
