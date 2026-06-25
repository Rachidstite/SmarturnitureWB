import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestOperationalDecisionContract(unittest.TestCase):

    def test_default_values(self):
        from project_engineering.operational_decision_report import (
            OperationalDecisionReport,
        )

        report = OperationalDecisionReport()

        self.assertTrue(is_dataclass(OperationalDecisionReport))
        self.assertEqual(
            [field.name for field in fields(OperationalDecisionReport)],
            [
                "ready_for_operation",
                "ready_for_installation",
                "ready_for_service",
                "warnings",
                "violations",
            ],
        )
        self.assertTrue(report.ready_for_operation)
        self.assertTrue(report.ready_for_installation)
        self.assertTrue(report.ready_for_service)
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.violations, [])

    def test_warnings_and_violations(self):
        from project_engineering.operational_decision_report import (
            OperationalDecisionReport,
        )

        report = OperationalDecisionReport(
            warnings=["review required"],
            violations=["constraint violated"],
        )

        self.assertEqual(report.warnings, ["review required"])
        self.assertEqual(report.violations, ["constraint violated"])
        self.assertTrue(report.ready_for_operation)
        self.assertTrue(report.ready_for_installation)
        self.assertTrue(report.ready_for_service)

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.operational_decision_report"
        )

        source = inspect.getsource(module)
        self.assertIn("OperationalDecisionReport", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.operational_decision_report"
        )

        source = inspect.getsource(module)
        for token in (
            "manufacturing",
            "cost",
            "FreeCAD",
            "operational_capability_contract",
            "operational_clearance_contract",
            "motion_contract",
            "accessibility_contract",
            "installation_sequence_contract",
            "serviceability_contract",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
