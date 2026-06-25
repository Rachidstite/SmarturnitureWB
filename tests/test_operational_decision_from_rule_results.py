import importlib
import inspect
import re
import unittest

from project_engineering.operational_decision_from_rule_results import (
    build_operational_decision_from_rule_results,
)
from project_engineering.operational_rule_result import OperationalRuleResult


class TestOperationalDecisionFromRuleResults(unittest.TestCase):
    def test_empty_results_produce_ready_decision(self):
        report = build_operational_decision_from_rule_results([])

        self.assertTrue(report.ready_for_operation)
        self.assertTrue(report.ready_for_installation)
        self.assertTrue(report.ready_for_service)
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.violations, [])

    def test_passed_results_produce_ready_decision(self):
        results = [
            OperationalRuleResult(
                rule_id="RULE-1",
                capability="operational_capability",
                component_id="cabinet-1",
                passed=True,
                severity="info",
                message="",
                source="src-1",
            ),
            OperationalRuleResult(
                rule_id="RULE-2",
                capability="motion",
                component_id="cabinet-2",
                passed=True,
                severity="info",
                message="",
                source="src-2",
            ),
        ]

        report = build_operational_decision_from_rule_results(results)

        self.assertTrue(report.ready_for_operation)
        self.assertTrue(report.ready_for_installation)
        self.assertTrue(report.ready_for_service)
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.violations, [])

    def test_warning_results_populate_warnings_without_failing_readiness(self):
        results = [
            OperationalRuleResult(
                rule_id="RULE-W1",
                capability="accessibility",
                component_id="cabinet-1",
                passed=True,
                severity="warning",
                message="review access zone",
            ),
            OperationalRuleResult(
                rule_id="RULE-W2",
                capability="serviceability",
                component_id="cabinet-2",
                passed=False,
                severity="warning",
                message="service access is limited",
            ),
        ]

        report = build_operational_decision_from_rule_results(results)

        self.assertTrue(report.ready_for_operation)
        self.assertTrue(report.ready_for_installation)
        self.assertTrue(report.ready_for_service)
        self.assertEqual(
            report.warnings,
            ["review access zone", "service access is limited"],
        )
        self.assertEqual(report.violations, [])

    def test_error_results_fail_all_ready_flags_and_populate_violations(self):
        results = [
            OperationalRuleResult(
                rule_id="RULE-E1",
                capability="clearance",
                component_id="cabinet-1",
                passed=False,
                severity="error",
                message="clearance missing",
            ),
            OperationalRuleResult(
                rule_id="RULE-E2",
                capability="motion",
                component_id="cabinet-2",
                passed=True,
                severity="info",
                message="",
            ),
        ]

        report = build_operational_decision_from_rule_results(results)

        self.assertFalse(report.ready_for_operation)
        self.assertFalse(report.ready_for_installation)
        self.assertFalse(report.ready_for_service)
        self.assertEqual(report.violations, ["clearance missing"])
        self.assertEqual(report.warnings, [])

    def test_empty_messages_are_ignored(self):
        results = [
            OperationalRuleResult(
                rule_id="RULE-W3",
                capability="accessibility",
                component_id="cabinet-1",
                passed=True,
                severity="warning",
                message="",
            ),
            OperationalRuleResult(
                rule_id="RULE-E3",
                capability="serviceability",
                component_id="cabinet-2",
                passed=False,
                severity="error",
                message="",
            ),
        ]

        report = build_operational_decision_from_rule_results(results)

        self.assertTrue(report.ready_for_operation is False)
        self.assertTrue(report.ready_for_installation is False)
        self.assertTrue(report.ready_for_service is False)
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.violations, [])

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.operational_decision_from_rule_results"
        )
        source = inspect.getsource(module)

        self.assertIn("build_operational_decision_from_rule_results", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.operational_decision_from_rule_results"
        )
        source = inspect.getsource(module)

        for token in (
            "manufacturing",
            "cost",
            "exports",
            "FreeCAD",
            "operational_capability_contract",
            "operational_clearance_contract",
            "motion_contract",
            "accessibility_contract",
            "installation_sequence_contract",
            "serviceability_contract",
            "operational_capability_satisfied_rule",
            "UI",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_function_is_generic_and_component_agnostic(self):
        signature = inspect.signature(build_operational_decision_from_rule_results)
        self.assertEqual(list(signature.parameters), ["results"])

        report = build_operational_decision_from_rule_results(
            [
                OperationalRuleResult(
                    rule_id="RULE-GENERIC",
                    capability="generic_capability",
                    component_id="component-x",
                    passed=True,
                )
            ]
        )

        self.assertTrue(report.ready_for_operation)
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.violations, [])


if __name__ == "__main__":
    unittest.main()
