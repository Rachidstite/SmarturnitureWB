import importlib
import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestOperationalClearanceContract(unittest.TestCase):

    def test_empty_report_defaults_to_satisfied(self):
        from project_engineering.operational_clearance_contract import (
            OperationalClearanceReport,
        )

        report = OperationalClearanceReport()

        self.assertTrue(is_dataclass(OperationalClearanceReport))
        self.assertEqual(
            [field.name for field in fields(OperationalClearanceReport)],
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

    def test_requirement_stores_required_operational_clearance_fields(self):
        from project_engineering.operational_clearance_contract import (
            OperationalClearanceRequirement,
        )

        requirement = OperationalClearanceRequirement(
            component_id="DOOR-1",
            required_clearance_mm=32.0,
            direction="swing",
            purpose="allow door opening",
            source="ADR-XYZ",
        )

        self.assertTrue(is_dataclass(OperationalClearanceRequirement))
        self.assertEqual(
            [field.name for field in fields(OperationalClearanceRequirement)],
            [
                "component_id",
                "required_clearance_mm",
                "direction",
                "purpose",
                "source",
            ],
        )
        self.assertEqual(requirement.component_id, "DOOR-1")
        self.assertEqual(requirement.required_clearance_mm, 32.0)
        self.assertEqual(requirement.direction, "swing")
        self.assertEqual(requirement.purpose, "allow door opening")
        self.assertEqual(requirement.source, "ADR-XYZ")

    def test_report_can_hold_multiple_requirements(self):
        from project_engineering.operational_clearance_contract import (
            OperationalClearanceReport,
            OperationalClearanceRequirement,
        )

        report = OperationalClearanceReport(
            requirements=[
                OperationalClearanceRequirement(
                    component_id="DOOR-1",
                    required_clearance_mm=32.0,
                    direction="swing",
                    purpose="allow door opening",
                ),
                OperationalClearanceRequirement(
                    component_id="DRAWER-1",
                    required_clearance_mm=450.0,
                    direction="slide",
                    purpose="allow drawer extension",
                ),
            ]
        )

        self.assertEqual(len(report.requirements), 2)
        self.assertEqual(report.requirements[0].component_id, "DOOR-1")
        self.assertEqual(report.requirements[1].component_id, "DRAWER-1")
        self.assertTrue(report.is_satisfied)

    def test_violations_only_make_report_unsatisfied_when_explicitly_constructed_that_way(self):
        from project_engineering.operational_clearance_contract import (
            OperationalClearanceReport,
        )

        satisfied_report = OperationalClearanceReport(
            violations=["clearance below requirement"],
        )
        unsatisfied_report = OperationalClearanceReport(
            is_satisfied=False,
            violations=["clearance below requirement"],
        )

        self.assertTrue(satisfied_report.is_satisfied)
        self.assertFalse(unsatisfied_report.is_satisfied)
        self.assertEqual(unsatisfied_report.violations, ["clearance below requirement"])

    def test_contract_is_generic_and_does_not_require_door_or_drawer_fields(self):
        from project_engineering.operational_clearance_contract import (
            OperationalClearanceRequirement,
            OperationalClearanceReport,
        )

        requirement_fields = [field.name for field in fields(OperationalClearanceRequirement)]
        report_fields = [field.name for field in fields(OperationalClearanceReport)]

        for token in (
            "door",
            "drawer",
            "hinge",
            "slide",
            "shelf",
            "panel",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, " ".join(requirement_fields + report_fields).lower())

    def test_module_imports_without_freecad(self):
        module = importlib.import_module("project_engineering.operational_clearance_contract")

        source = inspect.getsource(module)
        self.assertIn("OperationalClearanceRequirement", source)
        self.assertIn("OperationalClearanceReport", source)
        self.assertNotIn("FreeCAD", source)


if __name__ == "__main__":
    unittest.main()
