import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestAccessibilityContract(unittest.TestCase):

    def test_empty_report_defaults_to_satisfied(self):
        from project_engineering.accessibility_contract import AccessibilityReport

        report = AccessibilityReport()

        self.assertTrue(is_dataclass(AccessibilityReport))
        self.assertEqual(
            [field.name for field in fields(AccessibilityReport)],
            [
                "requirements",
                "is_satisfied",
                "violations",
                "warnings",
            ],
        )
        self.assertTrue(report.is_satisfied)
        self.assertEqual(report.requirements, [])
        self.assertEqual(report.violations, [])
        self.assertEqual(report.warnings, [])

    def test_requirement_stores_accessibility_fields(self):
        from project_engineering.accessibility_contract import AccessibilityRequirement

        requirement = AccessibilityRequirement(
            component_id="COMP-1",
            access_type="service",
            access_zone="rear",
            required_access_mm=600.0,
            purpose="allow inspection",
            source="ADR-P2",
        )

        self.assertTrue(is_dataclass(AccessibilityRequirement))
        self.assertEqual(
            [field.name for field in fields(AccessibilityRequirement)],
            [
                "component_id",
                "access_type",
                "access_zone",
                "required_access_mm",
                "purpose",
                "source",
            ],
        )
        self.assertEqual(requirement.component_id, "COMP-1")
        self.assertEqual(requirement.access_type, "service")
        self.assertEqual(requirement.access_zone, "rear")
        self.assertEqual(requirement.required_access_mm, 600.0)
        self.assertEqual(requirement.purpose, "allow inspection")
        self.assertEqual(requirement.source, "ADR-P2")

    def test_report_can_hold_multiple_requirements(self):
        from project_engineering.accessibility_contract import (
            AccessibilityReport,
            AccessibilityRequirement,
        )

        report = AccessibilityReport(
            requirements=[
                AccessibilityRequirement(
                    component_id="COMP-1",
                    access_type="service",
                    access_zone="rear",
                    required_access_mm=600.0,
                    purpose="allow inspection",
                ),
                AccessibilityRequirement(
                    component_id="COMP-2",
                    access_type="assembly",
                    access_zone="top",
                    required_access_mm=300.0,
                    purpose="allow assembly",
                ),
            ]
        )

        self.assertEqual(len(report.requirements), 2)
        self.assertEqual(report.requirements[0].component_id, "COMP-1")
        self.assertEqual(report.requirements[1].component_id, "COMP-2")
        self.assertTrue(report.is_satisfied)

    def test_violations_do_not_change_satisfied_state_unless_explicitly_passed(self):
        from project_engineering.accessibility_contract import AccessibilityReport

        satisfied_report = AccessibilityReport(
            violations=["access blocked"],
        )
        unsatisfied_report = AccessibilityReport(
            is_satisfied=False,
            violations=["access blocked"],
        )

        self.assertTrue(satisfied_report.is_satisfied)
        self.assertFalse(unsatisfied_report.is_satisfied)
        self.assertEqual(unsatisfied_report.violations, ["access blocked"])

    def test_contract_is_generic_and_does_not_require_specialized_fields(self):
        from project_engineering.accessibility_contract import (
            AccessibilityRequirement,
            AccessibilityReport,
        )

        field_names = " ".join(
            [field.name for field in fields(AccessibilityRequirement)]
            + [field.name for field in fields(AccessibilityReport)]
        ).lower()

        for token in (
            "door",
            "drawer",
            "hinge",
            "slide",
            "shelf",
            "panel",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, field_names)

    def test_module_imports_without_freecad(self):
        module = importlib.import_module("project_engineering.accessibility_contract")

        source = inspect.getsource(module)
        self.assertIn("AccessibilityRequirement", source)
        self.assertIn("AccessibilityReport", source)
        self.assertNotIn("FreeCAD", source)

    def test_accessibility_contract_does_not_import_banned_layers(self):
        module = importlib.import_module("project_engineering.accessibility_contract")

        source = inspect.getsource(module)
        for token in (
            "operational_clearance_contract",
            "motion_contract",
            "manufacturing",
            "cost_intelligence",
            "exports",
            "CNC",
            "FreeCAD",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
