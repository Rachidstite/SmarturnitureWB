import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestServiceabilityContract(unittest.TestCase):

    def test_empty_report_defaults_to_satisfied(self):
        from project_engineering.serviceability_contract import ServiceabilityReport

        report = ServiceabilityReport()

        self.assertTrue(is_dataclass(ServiceabilityReport))
        self.assertEqual(
            [field.name for field in fields(ServiceabilityReport)],
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

    def test_requirement_stores_serviceability_fields(self):
        from project_engineering.serviceability_contract import (
            ServiceabilityRequirement,
        )

        requirement = ServiceabilityRequirement(
            component_id="COMP-1",
            service_type="repair",
            service_zone="rear",
            required_access_mm=550.0,
            reason="must be repairable in place",
            purpose="allow service access",
            source="ADR-P2",
        )

        self.assertTrue(is_dataclass(ServiceabilityRequirement))
        self.assertEqual(
            [field.name for field in fields(ServiceabilityRequirement)],
            [
                "component_id",
                "service_type",
                "service_zone",
                "required_access_mm",
                "reason",
                "purpose",
                "source",
            ],
        )
        self.assertEqual(requirement.component_id, "COMP-1")
        self.assertEqual(requirement.service_type, "repair")
        self.assertEqual(requirement.service_zone, "rear")
        self.assertEqual(requirement.required_access_mm, 550.0)
        self.assertEqual(requirement.reason, "must be repairable in place")
        self.assertEqual(requirement.purpose, "allow service access")
        self.assertEqual(requirement.source, "ADR-P2")

    def test_report_can_hold_multiple_requirements(self):
        from project_engineering.serviceability_contract import (
            ServiceabilityReport,
            ServiceabilityRequirement,
        )

        report = ServiceabilityReport(
            requirements=[
                ServiceabilityRequirement(
                    component_id="COMP-1",
                    service_type="repair",
                    service_zone="rear",
                    required_access_mm=550.0,
                    reason="must be repairable in place",
                    purpose="allow service access",
                ),
                ServiceabilityRequirement(
                    component_id="COMP-2",
                    service_type="replace",
                    service_zone="front",
                    required_access_mm=300.0,
                    reason="replace without disassembly",
                    purpose="allow replacement",
                ),
            ]
        )

        self.assertEqual(len(report.requirements), 2)
        self.assertEqual(report.requirements[0].component_id, "COMP-1")
        self.assertEqual(report.requirements[1].component_id, "COMP-2")
        self.assertTrue(report.is_satisfied)

    def test_violations_do_not_change_satisfied_state_unless_explicitly_passed(self):
        from project_engineering.serviceability_contract import ServiceabilityReport

        satisfied_report = ServiceabilityReport(
            violations=["service access blocked"],
        )
        unsatisfied_report = ServiceabilityReport(
            is_satisfied=False,
            violations=["service access blocked"],
        )

        self.assertTrue(satisfied_report.is_satisfied)
        self.assertFalse(unsatisfied_report.is_satisfied)
        self.assertEqual(
            unsatisfied_report.violations,
            ["service access blocked"],
        )

    def test_contract_is_generic_and_does_not_require_specialized_fields(self):
        from project_engineering.serviceability_contract import (
            ServiceabilityRequirement,
            ServiceabilityReport,
        )

        field_names = " ".join(
            [field.name for field in fields(ServiceabilityRequirement)]
            + [field.name for field in fields(ServiceabilityReport)]
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
        module = importlib.import_module("project_engineering.serviceability_contract")

        source = inspect.getsource(module)
        self.assertIn("ServiceabilityRequirement", source)
        self.assertIn("ServiceabilityReport", source)
        self.assertNotIn("FreeCAD", source)

    def test_contract_does_not_import_banned_layers(self):
        module = importlib.import_module("project_engineering.serviceability_contract")

        source = inspect.getsource(module)
        for token in (
            "operational_clearance_contract",
            "motion_contract",
            "accessibility_contract",
            "installation_sequence_contract",
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
