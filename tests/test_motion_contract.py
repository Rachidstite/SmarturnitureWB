import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestMotionContract(unittest.TestCase):

    def test_empty_report_defaults_to_satisfied(self):
        from project_engineering.motion_contract import MotionReport

        report = MotionReport()

        self.assertTrue(is_dataclass(MotionReport))
        self.assertEqual(
            [field.name for field in fields(MotionReport)],
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

    def test_requirement_stores_motion_fields(self):
        from project_engineering.motion_contract import MotionRequirement

        requirement = MotionRequirement(
            component_id="COMP-1",
            motion_type="rotate",
            axis="Z",
            required_range=90.0,
            unit="deg",
            purpose="allow operation",
            source="ADR-P2",
        )

        self.assertTrue(is_dataclass(MotionRequirement))
        self.assertEqual(
            [field.name for field in fields(MotionRequirement)],
            [
                "component_id",
                "motion_type",
                "axis",
                "required_range",
                "unit",
                "purpose",
                "source",
            ],
        )
        self.assertEqual(requirement.component_id, "COMP-1")
        self.assertEqual(requirement.motion_type, "rotate")
        self.assertEqual(requirement.axis, "Z")
        self.assertEqual(requirement.required_range, 90.0)
        self.assertEqual(requirement.unit, "deg")
        self.assertEqual(requirement.purpose, "allow operation")
        self.assertEqual(requirement.source, "ADR-P2")

    def test_report_can_hold_multiple_motion_requirements(self):
        from project_engineering.motion_contract import MotionReport, MotionRequirement

        report = MotionReport(
            requirements=[
                MotionRequirement(
                    component_id="COMP-1",
                    motion_type="rotate",
                    axis="Z",
                    required_range=90.0,
                    unit="deg",
                    purpose="allow operation",
                ),
                MotionRequirement(
                    component_id="COMP-2",
                    motion_type="slide",
                    axis="X",
                    required_range=450.0,
                    unit="mm",
                    purpose="allow movement",
                ),
            ]
        )

        self.assertEqual(len(report.requirements), 2)
        self.assertEqual(report.requirements[0].component_id, "COMP-1")
        self.assertEqual(report.requirements[1].component_id, "COMP-2")
        self.assertTrue(report.is_satisfied)

    def test_violations_do_not_change_satisfied_state_unless_explicitly_passed(self):
        from project_engineering.motion_contract import MotionReport

        satisfied_report = MotionReport(violations=["motion below minimum"])
        unsatisfied_report = MotionReport(
            is_satisfied=False,
            violations=["motion below minimum"],
        )

        self.assertTrue(satisfied_report.is_satisfied)
        self.assertFalse(unsatisfied_report.is_satisfied)
        self.assertEqual(unsatisfied_report.violations, ["motion below minimum"])

    def test_contract_is_generic_and_does_not_require_specialized_fields(self):
        from project_engineering.motion_contract import MotionRequirement, MotionReport

        field_names = " ".join(
            [field.name for field in fields(MotionRequirement)]
            + [field.name for field in fields(MotionReport)]
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
        module = importlib.import_module("project_engineering.motion_contract")

        source = inspect.getsource(module)
        self.assertIn("MotionRequirement", source)
        self.assertIn("MotionReport", source)
        self.assertNotIn("FreeCAD", source)

    def test_motion_contract_does_not_import_banned_layers(self):
        module = importlib.import_module("project_engineering.motion_contract")

        source = inspect.getsource(module)
        for token in (
            "operational_clearance_contract",
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
