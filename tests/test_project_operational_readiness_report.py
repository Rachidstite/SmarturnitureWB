import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestProjectOperationalReadinessReport(unittest.TestCase):
    def test_default_report_is_ready(self):
        from project_engineering.project_operational_readiness_report import (
            ProjectOperationalReadinessReport,
        )

        report = ProjectOperationalReadinessReport(project_id="project-1")

        self.assertTrue(is_dataclass(ProjectOperationalReadinessReport))
        self.assertEqual(
            [field.name for field in fields(ProjectOperationalReadinessReport)],
            [
                "project_id",
                "ready_for_operation",
                "ready_for_installation",
                "ready_for_service",
                "overall_ready",
                "cabinet_count",
                "ready_cabinet_count",
                "warning_cabinet_count",
                "violation_cabinet_count",
                "warnings",
                "violations",
                "source",
            ],
        )
        self.assertEqual(report.project_id, "project-1")
        self.assertTrue(report.ready_for_operation)
        self.assertTrue(report.ready_for_installation)
        self.assertTrue(report.ready_for_service)
        self.assertTrue(report.overall_ready)
        self.assertEqual(report.cabinet_count, 0)
        self.assertEqual(report.ready_cabinet_count, 0)
        self.assertEqual(report.warning_cabinet_count, 0)
        self.assertEqual(report.violation_cabinet_count, 0)
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.violations, [])
        self.assertEqual(report.source, "")

    def test_stores_project_id_source_counters_warnings_and_violations(self):
        from project_engineering.project_operational_readiness_report import (
            ProjectOperationalReadinessReport,
        )

        report = ProjectOperationalReadinessReport(
            project_id="project-7",
            cabinet_count=10,
            ready_cabinet_count=7,
            warning_cabinet_count=2,
            violation_cabinet_count=1,
            warnings=["one cabinet needs review"],
            violations=["one cabinet has a violation"],
            source="project-readiness",
        )

        self.assertEqual(report.project_id, "project-7")
        self.assertEqual(report.cabinet_count, 10)
        self.assertEqual(report.ready_cabinet_count, 7)
        self.assertEqual(report.warning_cabinet_count, 2)
        self.assertEqual(report.violation_cabinet_count, 1)
        self.assertEqual(report.warnings, ["one cabinet needs review"])
        self.assertEqual(report.violations, ["one cabinet has a violation"])
        self.assertEqual(report.source, "project-readiness")

    def test_overall_ready_can_be_explicitly_false(self):
        from project_engineering.project_operational_readiness_report import (
            ProjectOperationalReadinessReport,
        )

        report = ProjectOperationalReadinessReport(
            project_id="project-9",
            overall_ready=False,
        )

        self.assertFalse(report.overall_ready)
        self.assertTrue(report.ready_for_operation)
        self.assertTrue(report.ready_for_installation)
        self.assertTrue(report.ready_for_service)

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.project_operational_readiness_report"
        )
        source = inspect.getsource(module)

        self.assertIn("ProjectOperationalReadinessReport", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.project_operational_readiness_report"
        )
        source = inspect.getsource(module)

        for token in (
            "manufacturing",
            "cost",
            "exports",
            "FreeCAD",
            "CabinetOperationalReadinessReport",
            "operational_capability_contract",
            "operational_decision_from_rule_results",
            "operational_rule_result",
            "operational_decision_report",
            "motion_contract",
            "accessibility_contract",
            "installation_sequence_contract",
            "serviceability_contract",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_contract_is_project_level_without_component_specific_fields(self):
        from project_engineering.project_operational_readiness_report import (
            ProjectOperationalReadinessReport,
        )

        signature = inspect.signature(ProjectOperationalReadinessReport)
        self.assertEqual(
            list(signature.parameters),
            [
                "project_id",
                "ready_for_operation",
                "ready_for_installation",
                "ready_for_service",
                "overall_ready",
                "cabinet_count",
                "ready_cabinet_count",
                "warning_cabinet_count",
                "violation_cabinet_count",
                "warnings",
                "violations",
                "source",
            ],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)


if __name__ == "__main__":
    unittest.main()
