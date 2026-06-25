import importlib
import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestOperationalCapabilityContract(unittest.TestCase):

    def test_empty_report_defaults_to_satisfied(self):
        from project_engineering.operational_capability_contract import (
            OperationalCapabilityReport,
        )

        report = OperationalCapabilityReport()

        self.assertTrue(is_dataclass(OperationalCapabilityReport))
        self.assertEqual(
            [field.name for field in fields(OperationalCapabilityReport)],
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

    def test_requirement_stores_required_fields(self):
        from project_engineering.operational_capability_contract import (
            OperationalCapabilityRequirement,
        )

        requirement = OperationalCapabilityRequirement(
            component_id="COMP-1",
            capability="rotate",
            purpose="allow operation",
            source="ADR-P2",
        )

        self.assertTrue(is_dataclass(OperationalCapabilityRequirement))
        self.assertEqual(
            [field.name for field in fields(OperationalCapabilityRequirement)],
            [
                "component_id",
                "capability",
                "purpose",
                "source",
            ],
        )
        self.assertEqual(requirement.component_id, "COMP-1")
        self.assertEqual(requirement.capability, "rotate")
        self.assertEqual(requirement.purpose, "allow operation")
        self.assertEqual(requirement.source, "ADR-P2")

    def test_report_can_hold_multiple_requirements(self):
        from project_engineering.operational_capability_contract import (
            OperationalCapabilityReport,
            OperationalCapabilityRequirement,
        )

        report = OperationalCapabilityReport(
            requirements=[
                OperationalCapabilityRequirement(
                    component_id="COMP-1",
                    capability="rotate",
                    purpose="allow operation",
                ),
                OperationalCapabilityRequirement(
                    component_id="COMP-2",
                    capability="extend",
                    purpose="allow extension",
                ),
            ]
        )

        self.assertEqual(len(report.requirements), 2)
        self.assertEqual(report.requirements[0].component_id, "COMP-1")
        self.assertEqual(report.requirements[1].component_id, "COMP-2")
        self.assertTrue(report.is_satisfied)

    def test_violations_do_not_change_satisfied_state_when_not_explicitly_set(self):
        from project_engineering.operational_capability_contract import (
            OperationalCapabilityReport,
        )

        report = OperationalCapabilityReport(
            violations=["requirement not met"],
        )
        explicit_failure = OperationalCapabilityReport(
            is_satisfied=False,
            violations=["requirement not met"],
        )

        self.assertTrue(report.is_satisfied)
        self.assertFalse(explicit_failure.is_satisfied)
        self.assertEqual(explicit_failure.violations, ["requirement not met"])

    def test_contract_is_generic_and_uses_only_generic_fields(self):
        from project_engineering.operational_capability_contract import (
            OperationalCapabilityRequirement,
            OperationalCapabilityReport,
        )

        self.assertEqual(
            [field.name for field in fields(OperationalCapabilityRequirement)],
            [
                "component_id",
                "capability",
                "purpose",
                "source",
            ],
        )
        self.assertEqual(
            [field.name for field in fields(OperationalCapabilityReport)],
            [
                "requirements",
                "is_satisfied",
                "violations",
                "warnings",
            ],
        )

    def test_module_imports_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.operational_capability_contract"
        )

        source = inspect.getsource(module)
        self.assertIn("OperationalCapabilityRequirement", source)
        self.assertIn("OperationalCapabilityReport", source)
        self.assertNotIn("FreeCAD", source)


if __name__ == "__main__":
    unittest.main()
