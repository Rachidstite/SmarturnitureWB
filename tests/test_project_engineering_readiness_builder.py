import importlib
import inspect
import re
import unittest

from project_engineering.operational_decision_report import OperationalDecisionReport
from project_engineering.project_engineering_readiness_report import (
    ProjectEngineeringReadinessReport,
)


class TestProjectEngineeringReadinessBuilder(unittest.TestCase):
    def test_builds_project_engineering_readiness_report(self):
        from project_engineering.project_engineering_readiness_builder import (
            build_project_engineering_readiness_report,
        )

        report = build_project_engineering_readiness_report(
            project_id="PROJECT-1",
            decision=OperationalDecisionReport(
                ready_for_operation=True,
                ready_for_installation=False,
                ready_for_service=False,
                warnings=["review note"],
                violations=["blocking issue"],
            ),
        )

        self.assertIsInstance(report, ProjectEngineeringReadinessReport)

    def test_copies_project_id(self):
        from project_engineering.project_engineering_readiness_builder import (
            build_project_engineering_readiness_report,
        )

        report = build_project_engineering_readiness_report(
            project_id="PROJECT-2",
            decision=OperationalDecisionReport(),
        )

        self.assertEqual(report.project_id, "PROJECT-2")

    def test_sets_ready_flags_from_decision_ready_for_operation(self):
        from project_engineering.project_engineering_readiness_builder import (
            build_project_engineering_readiness_report,
        )

        ready_report = build_project_engineering_readiness_report(
            project_id="PROJECT-3",
            decision=OperationalDecisionReport(ready_for_operation=True),
        )
        blocked_report = build_project_engineering_readiness_report(
            project_id="PROJECT-4",
            decision=OperationalDecisionReport(ready_for_operation=False),
        )

        self.assertTrue(ready_report.ready_for_engineering_release)
        self.assertTrue(ready_report.ready_for_manufacturing_handoff)
        self.assertFalse(blocked_report.ready_for_engineering_release)
        self.assertFalse(blocked_report.ready_for_manufacturing_handoff)

    def test_counts_blocking_violations(self):
        from project_engineering.project_engineering_readiness_builder import (
            build_project_engineering_readiness_report,
        )

        report = build_project_engineering_readiness_report(
            project_id="PROJECT-5",
            decision=OperationalDecisionReport(
                ready_for_operation=False,
                violations=["a", "b", "c"],
            ),
        )

        self.assertEqual(report.blocking_violation_count, 3)

    def test_counts_warnings(self):
        from project_engineering.project_engineering_readiness_builder import (
            build_project_engineering_readiness_report,
        )

        report = build_project_engineering_readiness_report(
            project_id="PROJECT-6",
            decision=OperationalDecisionReport(
                ready_for_operation=True,
                warnings=["warn-1", "warn-2"],
            ),
        )

        self.assertEqual(report.warning_count, 2)

    def test_sets_source_correctly(self):
        from project_engineering.project_engineering_readiness_builder import (
            build_project_engineering_readiness_report,
        )

        report = build_project_engineering_readiness_report(
            project_id="PROJECT-7",
            decision=OperationalDecisionReport(),
        )

        self.assertEqual(report.source, "project-engineering-readiness-builder")

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.project_engineering_readiness_builder"
        )
        source = inspect.getsource(module)

        self.assertIn("build_project_engineering_readiness_report", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.project_engineering_readiness_builder"
        )
        source = inspect.getsource(module)

        for token in (
            "rule",
            "decision reducer",
            "geometry",
            "spatial analysis",
            "manufacturing logic",
            "cost logic",
            "CNC",
            "export",
            "FurnitureProject",
            "CabinetPlacement",
            "SceneGraph",
            "FreeCAD",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_function_signature_remains_generic(self):
        from project_engineering.project_engineering_readiness_builder import (
            build_project_engineering_readiness_report,
        )

        signature = inspect.signature(build_project_engineering_readiness_report)
        self.assertEqual(list(signature.parameters), ["project_id", "decision"])
        self.assertNotIn("self", signature.parameters)
        self.assertNotIn("cls", signature.parameters)

    def test_does_not_contain_engine_terminology(self):
        module = importlib.import_module(
            "project_engineering.project_engineering_readiness_builder"
        )
        source = inspect.getsource(module)

        self.assertNotIn("ProjectEngineeringEngine", source)
        self.assertNotIn("ProjectValidationEngine", source)
        self.assertNotIn("ProjectOperationalValidationBuilder", source)
        self.assertIsNone(re.search(r"\bEngine\b", source))


if __name__ == "__main__":
    unittest.main()
