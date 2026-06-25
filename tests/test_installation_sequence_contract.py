import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestInstallationSequenceContract(unittest.TestCase):

    def test_empty_report_defaults_to_satisfied(self):
        from project_engineering.installation_sequence_contract import (
            InstallationSequenceReport,
        )

        report = InstallationSequenceReport()

        self.assertTrue(is_dataclass(InstallationSequenceReport))
        self.assertEqual(
            [field.name for field in fields(InstallationSequenceReport)],
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

    def test_requirement_stores_installation_sequence_fields(self):
        from project_engineering.installation_sequence_contract import (
            InstallationSequenceRequirement,
        )

        requirement = InstallationSequenceRequirement(
            component_id="COMP-1",
            prerequisite_id="PRE-1",
            sequence_type="preinstall",
            reason="must exist first",
            purpose="allow safe installation",
            source="ADR-P2",
        )

        self.assertTrue(is_dataclass(InstallationSequenceRequirement))
        self.assertEqual(
            [field.name for field in fields(InstallationSequenceRequirement)],
            [
                "component_id",
                "prerequisite_id",
                "sequence_type",
                "reason",
                "purpose",
                "source",
            ],
        )
        self.assertEqual(requirement.component_id, "COMP-1")
        self.assertEqual(requirement.prerequisite_id, "PRE-1")
        self.assertEqual(requirement.sequence_type, "preinstall")
        self.assertEqual(requirement.reason, "must exist first")
        self.assertEqual(requirement.purpose, "allow safe installation")
        self.assertEqual(requirement.source, "ADR-P2")

    def test_report_can_hold_multiple_requirements(self):
        from project_engineering.installation_sequence_contract import (
            InstallationSequenceReport,
            InstallationSequenceRequirement,
        )

        report = InstallationSequenceReport(
            requirements=[
                InstallationSequenceRequirement(
                    component_id="COMP-1",
                    prerequisite_id="PRE-1",
                    sequence_type="preinstall",
                    reason="must exist first",
                    purpose="allow safe installation",
                ),
                InstallationSequenceRequirement(
                    component_id="COMP-2",
                    prerequisite_id="PRE-2",
                    sequence_type="postinstall",
                    reason="depends on prior step",
                    purpose="allow service access",
                ),
            ]
        )

        self.assertEqual(len(report.requirements), 2)
        self.assertEqual(report.requirements[0].component_id, "COMP-1")
        self.assertEqual(report.requirements[1].component_id, "COMP-2")
        self.assertTrue(report.is_satisfied)

    def test_violations_do_not_change_satisfied_state_unless_explicitly_passed(self):
        from project_engineering.installation_sequence_contract import (
            InstallationSequenceReport,
        )

        satisfied_report = InstallationSequenceReport(
            violations=["prerequisite missing"],
        )
        unsatisfied_report = InstallationSequenceReport(
            is_satisfied=False,
            violations=["prerequisite missing"],
        )

        self.assertTrue(satisfied_report.is_satisfied)
        self.assertFalse(unsatisfied_report.is_satisfied)
        self.assertEqual(unsatisfied_report.violations, ["prerequisite missing"])

    def test_contract_is_generic_and_does_not_require_specialized_fields(self):
        from project_engineering.installation_sequence_contract import (
            InstallationSequenceRequirement,
            InstallationSequenceReport,
        )

        field_names = " ".join(
            [field.name for field in fields(InstallationSequenceRequirement)]
            + [field.name for field in fields(InstallationSequenceReport)]
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
        module = importlib.import_module(
            "project_engineering.installation_sequence_contract"
        )

        source = inspect.getsource(module)
        self.assertIn("InstallationSequenceRequirement", source)
        self.assertIn("InstallationSequenceReport", source)
        self.assertNotIn("FreeCAD", source)

    def test_contract_does_not_import_banned_layers(self):
        module = importlib.import_module(
            "project_engineering.installation_sequence_contract"
        )

        source = inspect.getsource(module)
        for token in (
            "operational_clearance_contract",
            "motion_contract",
            "accessibility_contract",
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
