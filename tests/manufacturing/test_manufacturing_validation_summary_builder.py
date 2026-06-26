import inspect
import unittest


class TestManufacturingValidationSummaryBuilder(unittest.TestCase):

    def test_builds_manufacturing_validation_summary_report(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )
        from manufacturing.manufacturing_validation_summary_builder import (
            build_manufacturing_validation_summary_report,
        )
        from manufacturing.manufacturing_validation_summary_report import (
            ManufacturingValidationSummaryReport,
        )
        from project_engineering.operational_rule_result import (
            OperationalRuleResult,
        )

        validation_report = build_manufacturing_validation_report(
            [
                OperationalRuleResult(
                    rule_id="R1",
                    capability="C1",
                    component_id="A",
                    passed=True,
                    severity="info",
                ),
                OperationalRuleResult(
                    rule_id="R2",
                    capability="C2",
                    component_id="B",
                    passed=False,
                    severity="error",
                    message="Blocking issue",
                ),
                OperationalRuleResult(
                    rule_id="R3",
                    capability="C3",
                    component_id="C",
                    passed=False,
                    severity="warning",
                    message="Warning issue",
                ),
            ]
        )

        summary_report = build_manufacturing_validation_summary_report(
            validation_report,
            [
                OperationalRuleResult(
                    rule_id="R1",
                    capability="C1",
                    component_id="A",
                    passed=True,
                    severity="info",
                ),
                OperationalRuleResult(
                    rule_id="R2",
                    capability="C2",
                    component_id="B",
                    passed=False,
                    severity="error",
                    message="Blocking issue",
                ),
                OperationalRuleResult(
                    rule_id="R3",
                    capability="C3",
                    component_id="C",
                    passed=False,
                    severity="warning",
                    message="Warning issue",
                ),
            ],
        )

        self.assertIsInstance(summary_report, ManufacturingValidationSummaryReport)
        self.assertFalse(summary_report.ready_for_manufacturing)
        self.assertEqual(summary_report.total_rule_count, 3)
        self.assertEqual(summary_report.passed_rule_count, 1)
        self.assertEqual(summary_report.failed_rule_count, 2)
        self.assertEqual(summary_report.warning_count, 1)
        self.assertEqual(summary_report.blocking_issue_count, 1)
        self.assertEqual(summary_report.blocking_messages, ["Blocking issue"])
        self.assertEqual(summary_report.warning_messages, ["Warning issue"])
        self.assertEqual(
            summary_report.source,
            "manufacturing-validation-summary-builder",
        )

    def test_copies_count_fields_from_validation_report(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )
        from manufacturing.manufacturing_validation_summary_builder import (
            build_manufacturing_validation_summary_report,
        )
        from project_engineering.operational_rule_result import (
            OperationalRuleResult,
        )

        validation_report = build_manufacturing_validation_report(
            [
                OperationalRuleResult(
                    rule_id="R1",
                    capability="C1",
                    component_id="A",
                    passed=True,
                    severity="info",
                )
            ]
        )

        summary_report = build_manufacturing_validation_summary_report(
            validation_report,
            [],
        )

        self.assertEqual(summary_report.ready_for_manufacturing, validation_report.ready_for_manufacturing)
        self.assertEqual(summary_report.total_rule_count, validation_report.total_rule_count)
        self.assertEqual(summary_report.passed_rule_count, validation_report.passed_rule_count)
        self.assertEqual(summary_report.failed_rule_count, validation_report.failed_rule_count)
        self.assertEqual(summary_report.warning_count, validation_report.warning_count)
        self.assertEqual(summary_report.blocking_issue_count, validation_report.blocking_issue_count)

    def test_collects_blocking_messages_from_failed_error_rule_results(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )
        from manufacturing.manufacturing_validation_summary_builder import (
            build_manufacturing_validation_summary_report,
        )
        from project_engineering.operational_rule_result import (
            OperationalRuleResult,
        )

        rule_results = [
            OperationalRuleResult(
                rule_id="R1",
                capability="C1",
                component_id="A",
                passed=False,
                severity="error",
                message="Blocking issue one",
            ),
            OperationalRuleResult(
                rule_id="R2",
                capability="C2",
                component_id="B",
                passed=False,
                severity="error",
                message="Blocking issue two",
            ),
            OperationalRuleResult(
                rule_id="R3",
                capability="C3",
                component_id="C",
                passed=False,
                severity="warning",
                message="Warning issue",
            ),
        ]
        validation_report = build_manufacturing_validation_report(rule_results)

        summary_report = build_manufacturing_validation_summary_report(
            validation_report,
            rule_results,
        )

        self.assertEqual(
            summary_report.blocking_messages,
            ["Blocking issue one", "Blocking issue two"],
        )

    def test_collects_warning_messages_from_warning_rule_results(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )
        from manufacturing.manufacturing_validation_summary_builder import (
            build_manufacturing_validation_summary_report,
        )
        from project_engineering.operational_rule_result import (
            OperationalRuleResult,
        )

        rule_results = [
            OperationalRuleResult(
                rule_id="R1",
                capability="C1",
                component_id="A",
                passed=False,
                severity="warning",
                message="Warning issue one",
            ),
            OperationalRuleResult(
                rule_id="R2",
                capability="C2",
                component_id="B",
                passed=False,
                severity="warning",
                message="Warning issue two",
            ),
            OperationalRuleResult(
                rule_id="R3",
                capability="C3",
                component_id="C",
                passed=False,
                severity="error",
                message="Blocking issue",
            ),
        ]
        validation_report = build_manufacturing_validation_report(rule_results)

        summary_report = build_manufacturing_validation_summary_report(
            validation_report,
            rule_results,
        )

        self.assertEqual(
            summary_report.warning_messages,
            ["Warning issue one", "Warning issue two"],
        )

    def test_does_not_include_info_messages(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )
        from manufacturing.manufacturing_validation_summary_builder import (
            build_manufacturing_validation_summary_report,
        )
        from project_engineering.operational_rule_result import (
            OperationalRuleResult,
        )

        rule_results = [
            OperationalRuleResult(
                rule_id="R1",
                capability="C1",
                component_id="A",
                passed=True,
                severity="info",
                message="Info message",
            ),
            OperationalRuleResult(
                rule_id="R2",
                capability="C2",
                component_id="B",
                passed=False,
                severity="error",
                message="Blocking issue",
            ),
        ]
        validation_report = build_manufacturing_validation_report(rule_results)

        summary_report = build_manufacturing_validation_summary_report(
            validation_report,
            rule_results,
        )

        self.assertNotIn("Info message", summary_report.blocking_messages)
        self.assertNotIn("Info message", summary_report.warning_messages)

    def test_does_not_include_passed_error_results_as_blocking_messages(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )
        from manufacturing.manufacturing_validation_summary_builder import (
            build_manufacturing_validation_summary_report,
        )
        from project_engineering.operational_rule_result import (
            OperationalRuleResult,
        )

        rule_results = [
            OperationalRuleResult(
                rule_id="R1",
                capability="C1",
                component_id="A",
                passed=True,
                severity="error",
                message="Recovered error",
            ),
            OperationalRuleResult(
                rule_id="R2",
                capability="C2",
                component_id="B",
                passed=False,
                severity="error",
                message="Blocking issue",
            ),
        ]
        validation_report = build_manufacturing_validation_report(rule_results)

        summary_report = build_manufacturing_validation_summary_report(
            validation_report,
            rule_results,
        )

        self.assertNotIn("Recovered error", summary_report.blocking_messages)
        self.assertIn("Blocking issue", summary_report.blocking_messages)

    def test_source_is_correct(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )
        from manufacturing.manufacturing_validation_summary_builder import (
            build_manufacturing_validation_summary_report,
        )
        from project_engineering.operational_rule_result import (
            OperationalRuleResult,
        )

        validation_report = build_manufacturing_validation_report(
            [
                OperationalRuleResult(
                    rule_id="R1",
                    capability="C1",
                    component_id="A",
                    passed=True,
                    severity="info",
                )
            ]
        )

        summary_report = build_manufacturing_validation_summary_report(
            validation_report,
            [],
        )

        self.assertEqual(
            summary_report.source,
            "manufacturing-validation-summary-builder",
        )

    def test_import_without_freecad(self):
        import manufacturing.manufacturing_validation_summary_builder as module

        source = inspect.getsource(module)

        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        import manufacturing.manufacturing_validation_summary_builder as module

        source = inspect.getsource(module)

        for token in (
            "FreeCAD",
            "SceneGraph",
            "UI",
            "CNC",
            "export",
            "cost",
            "nesting",
            "geometry",
            "evaluate",
            "validate",
        ):
            self.assertNotIn(token, source)

    def test_function_signature_remains_generic(self):
        from manufacturing.manufacturing_validation_summary_builder import (
            build_manufacturing_validation_summary_report,
        )

        signature = inspect.signature(build_manufacturing_validation_summary_report)

        self.assertEqual(
            list(signature.parameters),
            ["validation_report", "rule_results"],
        )

    def test_existing_manufacturing_validation_report_tests_still_pass(self):
        from manufacturing.manufacturing_validation_report import (
            ManufacturingValidationReport,
        )

        report = ManufacturingValidationReport()

        self.assertFalse(report.ready_for_manufacturing)
        self.assertEqual(report.total_rule_count, 0)

    def test_existing_manufacturing_validation_builder_tests_still_pass(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )
        from project_engineering.operational_rule_result import (
            OperationalRuleResult,
        )

        report = build_manufacturing_validation_report(
            [
                OperationalRuleResult(
                    rule_id="R1",
                    capability="C1",
                    component_id="A",
                    passed=True,
                    severity="info",
                )
            ]
        )

        self.assertTrue(report.ready_for_manufacturing)
        self.assertEqual(report.total_rule_count, 1)

    def test_existing_manufacturing_validation_summary_report_tests_still_pass(self):
        from manufacturing.manufacturing_validation_summary_report import (
            ManufacturingValidationSummaryReport,
        )

        report = ManufacturingValidationSummaryReport()

        self.assertFalse(report.ready_for_manufacturing)
        self.assertEqual(report.blocking_messages, [])
        self.assertEqual(report.warning_messages, [])


if __name__ == "__main__":
    unittest.main()
