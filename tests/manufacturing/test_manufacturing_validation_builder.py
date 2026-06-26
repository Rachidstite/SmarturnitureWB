import importlib
import inspect
import re
import unittest

from project_engineering.operational_rule_result import OperationalRuleResult


class TestManufacturingValidationBuilder(unittest.TestCase):
    def test_builds_manufacturing_validation_report(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )
        from manufacturing.manufacturing_validation_report import (
            ManufacturingValidationReport,
        )

        report = build_manufacturing_validation_report(
            [
                OperationalRuleResult(
                    rule_id="RULE-1",
                    capability="manufacturing_material_readiness",
                    component_id="panel-1",
                    passed=True,
                    severity="info",
                )
            ]
        )

        self.assertIsInstance(report, ManufacturingValidationReport)

    def test_counts_total_rules(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )

        report = build_manufacturing_validation_report(
            [
                OperationalRuleResult(
                    rule_id="RULE-1",
                    capability="manufacturing_material_readiness",
                    component_id="panel-1",
                    passed=True,
                    severity="info",
                ),
                OperationalRuleResult(
                    rule_id="RULE-2",
                    capability="manufacturing_material_readiness",
                    component_id="panel-2",
                    passed=False,
                    severity="error",
                ),
            ]
        )

        self.assertEqual(report.total_rule_count, 2)

    def test_counts_passed_rules(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )

        report = build_manufacturing_validation_report(
            [
                OperationalRuleResult(
                    rule_id="RULE-1",
                    capability="manufacturing_material_readiness",
                    component_id="panel-1",
                    passed=True,
                    severity="info",
                ),
                OperationalRuleResult(
                    rule_id="RULE-2",
                    capability="manufacturing_material_readiness",
                    component_id="panel-2",
                    passed=True,
                    severity="warning",
                ),
                OperationalRuleResult(
                    rule_id="RULE-3",
                    capability="manufacturing_material_readiness",
                    component_id="panel-3",
                    passed=False,
                    severity="error",
                ),
            ]
        )

        self.assertEqual(report.passed_rule_count, 2)

    def test_counts_failed_rules(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )

        report = build_manufacturing_validation_report(
            [
                OperationalRuleResult(
                    rule_id="RULE-1",
                    capability="manufacturing_material_readiness",
                    component_id="panel-1",
                    passed=True,
                    severity="info",
                ),
                OperationalRuleResult(
                    rule_id="RULE-2",
                    capability="manufacturing_material_readiness",
                    component_id="panel-2",
                    passed=False,
                    severity="warning",
                ),
                OperationalRuleResult(
                    rule_id="RULE-3",
                    capability="manufacturing_material_readiness",
                    component_id="panel-3",
                    passed=False,
                    severity="error",
                ),
            ]
        )

        self.assertEqual(report.failed_rule_count, 2)

    def test_counts_warnings(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )

        report = build_manufacturing_validation_report(
            [
                OperationalRuleResult(
                    rule_id="RULE-1",
                    capability="manufacturing_material_readiness",
                    component_id="panel-1",
                    passed=True,
                    severity="warning",
                ),
                OperationalRuleResult(
                    rule_id="RULE-2",
                    capability="manufacturing_material_readiness",
                    component_id="panel-2",
                    passed=False,
                    severity="warning",
                ),
                OperationalRuleResult(
                    rule_id="RULE-3",
                    capability="manufacturing_material_readiness",
                    component_id="panel-3",
                    passed=False,
                    severity="error",
                ),
            ]
        )

        self.assertEqual(report.warning_count, 2)

    def test_counts_blocking_issues(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )

        report = build_manufacturing_validation_report(
            [
                OperationalRuleResult(
                    rule_id="RULE-1",
                    capability="manufacturing_material_readiness",
                    component_id="panel-1",
                    passed=False,
                    severity="error",
                ),
                OperationalRuleResult(
                    rule_id="RULE-2",
                    capability="manufacturing_material_readiness",
                    component_id="panel-2",
                    passed=False,
                    severity="warning",
                ),
            ]
        )

        self.assertEqual(report.blocking_issue_count, 1)

    def test_ready_for_manufacturing_is_true_when_no_blocking_issues(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )

        report = build_manufacturing_validation_report(
            [
                OperationalRuleResult(
                    rule_id="RULE-1",
                    capability="manufacturing_material_readiness",
                    component_id="panel-1",
                    passed=True,
                    severity="info",
                ),
                OperationalRuleResult(
                    rule_id="RULE-2",
                    capability="manufacturing_material_readiness",
                    component_id="panel-2",
                    passed=False,
                    severity="warning",
                ),
            ]
        )

        self.assertTrue(report.ready_for_manufacturing)

    def test_ready_for_manufacturing_is_false_when_blocking_issues_exist(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )

        report = build_manufacturing_validation_report(
            [
                OperationalRuleResult(
                    rule_id="RULE-1",
                    capability="manufacturing_material_readiness",
                    component_id="panel-1",
                    passed=False,
                    severity="error",
                )
            ]
        )

        self.assertFalse(report.ready_for_manufacturing)

    def test_sets_source_correctly(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )

        report = build_manufacturing_validation_report([])

        self.assertEqual(report.source, "manufacturing-validation-builder")

    def test_import_without_freecad(self):
        module = importlib.import_module("manufacturing.manufacturing_validation_builder")
        source = inspect.getsource(module)

        self.assertIn("build_manufacturing_validation_report", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("manufacturing.manufacturing_validation_builder")
        source = inspect.getsource(module)

        for token in (
            "geometry",
            "cost",
            "export",
            "CNC",
            "nesting",
            "SceneGraph",
            "FreeCAD",
            "decision",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))
        self.assertIsNone(re.search(r"\bEngine\b", source))

    def test_function_signature_remains_generic(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )

        signature = inspect.signature(build_manufacturing_validation_report)
        self.assertEqual(list(signature.parameters), ["rule_results"])
        self.assertNotIn("self", signature.parameters)
        self.assertNotIn("cls", signature.parameters)


if __name__ == "__main__":
    unittest.main()
