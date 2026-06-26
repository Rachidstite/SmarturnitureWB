import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestProjectSpatialSummaryReport(unittest.TestCase):
    def test_defaults_all_string_fields_to_empty_string(self):
        from project_engineering.project_spatial_summary_report import (
            ProjectSpatialSummaryReport,
        )

        report = ProjectSpatialSummaryReport()

        self.assertEqual(report.project_id, "")
        self.assertEqual(report.envelope_source, "")
        self.assertEqual(report.footprint_source, "")
        self.assertEqual(report.source, "")

    def test_defaults_counts_to_zero(self):
        from project_engineering.project_spatial_summary_report import (
            ProjectSpatialSummaryReport,
        )

        report = ProjectSpatialSummaryReport()

        self.assertEqual(report.adjacency_count, 0)
        self.assertEqual(report.alignment_count, 0)
        self.assertEqual(report.collision_count, 0)

    def test_defaults_has_collisions_to_false(self):
        from project_engineering.project_spatial_summary_report import (
            ProjectSpatialSummaryReport,
        )

        report = ProjectSpatialSummaryReport()

        self.assertFalse(report.has_collisions)

    def test_can_store_project_summary_values(self):
        from project_engineering.project_spatial_summary_report import (
            ProjectSpatialSummaryReport,
        )

        report = ProjectSpatialSummaryReport(
            project_id="PROJECT-1",
            envelope_source="envelope-aggregator",
            footprint_source="footprint-builder",
            adjacency_count=3,
            alignment_count=2,
            collision_count=1,
            has_collisions=True,
            source="spatial-intelligence",
        )

        self.assertEqual(report.project_id, "PROJECT-1")
        self.assertEqual(report.envelope_source, "envelope-aggregator")
        self.assertEqual(report.footprint_source, "footprint-builder")
        self.assertEqual(report.adjacency_count, 3)
        self.assertEqual(report.alignment_count, 2)
        self.assertEqual(report.collision_count, 1)
        self.assertTrue(report.has_collisions)
        self.assertEqual(report.source, "spatial-intelligence")

    def test_dataclass_fields_are_exact(self):
        from project_engineering.project_spatial_summary_report import (
            ProjectSpatialSummaryReport,
        )

        self.assertTrue(is_dataclass(ProjectSpatialSummaryReport))
        self.assertEqual(
            [field.name for field in fields(ProjectSpatialSummaryReport)],
            [
                "project_id",
                "envelope_source",
                "footprint_source",
                "adjacency_count",
                "alignment_count",
                "collision_count",
                "has_collisions",
                "source",
            ],
        )

        signature = inspect.signature(ProjectSpatialSummaryReport)
        self.assertEqual(
            list(signature.parameters),
            [
                "project_id",
                "envelope_source",
                "footprint_source",
                "adjacency_count",
                "alignment_count",
                "collision_count",
                "has_collisions",
                "source",
            ],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.project_spatial_summary_report"
        )
        source = inspect.getsource(module)

        self.assertIn("ProjectSpatialSummaryReport", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.project_spatial_summary_report"
        )
        source = inspect.getsource(module)

        for token in (
            "builder",
            "aggregator",
            "rule",
            "decision",
            "collision calculation",
            "layout",
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

    def test_does_not_contain_logic_keywords(self):
        module = importlib.import_module(
            "project_engineering.project_spatial_summary_report"
        )
        source = inspect.getsource(module)

        for token in (
            "aggregate",
            "builder",
            "rule",
            "decision",
            "calculate",
            "layout",
            "if ",
            "for ",
            "while ",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
