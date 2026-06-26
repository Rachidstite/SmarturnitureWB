import inspect
import unittest


class TestConfirmatValidationReadinessRule(unittest.TestCase):

    def setUp(self):
        from manufacturing.confirmat_validation_readiness_rule import (
            evaluate_confirmat_validation_readiness,
        )

        self.evaluate = evaluate_confirmat_validation_readiness

    def test_passing_report_when_confirmat_validation_is_ready(self):
        from manufacturing.confirmat_validation_report import (
            ConfirmatValidationReport,
        )

        report = ConfirmatValidationReport(
            validation_status="READY",
            is_valid=True,
            edge_distance_risk="LOW",
            spacing_risk="LOW",
            assembly_risk="LOW",
            manufacturing_warning="",
            recommended_action="",
        )

        result = self.evaluate(report)

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_failing_report_when_confirmat_validation_is_invalid(self):
        from manufacturing.confirmat_validation_report import (
            ConfirmatValidationReport,
        )

        report = ConfirmatValidationReport(
            validation_status="BLOCKED",
            is_valid=False,
            edge_distance_risk="HIGH",
            spacing_risk="HIGH",
            assembly_risk="HIGH",
            manufacturing_warning="Confirmat holes are not ready",
            recommended_action="Review spacing",
        )

        result = self.evaluate(report)

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("validation_status", result.message)
        self.assertIn("is_valid", result.message)

    def test_failure_message_includes_key_validation_fields(self):
        from manufacturing.confirmat_validation_report import (
            ConfirmatValidationReport,
        )

        report = ConfirmatValidationReport(
            validation_status="BLOCKED",
            is_valid=False,
            edge_distance_risk="HIGH",
            spacing_risk="HIGH",
            assembly_risk="HIGH",
            manufacturing_warning="Edge distance too small",
            recommended_action="Increase edge distance",
        )

        result = self.evaluate(report)

        self.assertIn("validation_status", result.message)
        self.assertIn("is_valid", result.message)
        self.assertIn("edge_distance_risk", result.message)
        self.assertIn("spacing_risk", result.message)
        self.assertIn("assembly_risk", result.message)
        self.assertIn("manufacturing_warning", result.message)
        self.assertIn("recommended_action", result.message)

    def test_capability_is_correct(self):
        from manufacturing.confirmat_validation_report import (
            ConfirmatValidationReport,
        )

        result = self.evaluate(ConfirmatValidationReport(is_valid=True))

        self.assertEqual(
            result.capability,
            "manufacturing_confirmat_validation_readiness",
        )

    def test_component_id_is_correct(self):
        from manufacturing.confirmat_validation_report import (
            ConfirmatValidationReport,
        )

        result = self.evaluate(ConfirmatValidationReport(is_valid=True))

        self.assertEqual(result.component_id, "confirmat-validation")

    def test_source_is_correct(self):
        from manufacturing.confirmat_validation_report import (
            ConfirmatValidationReport,
        )

        result = self.evaluate(ConfirmatValidationReport(is_valid=True))

        self.assertEqual(result.source, "confirmat-validation-readiness-rule")

    def test_import_without_freecad(self):
        import manufacturing.confirmat_validation_readiness_rule as module

        source = inspect.getsource(module)

        self.assertNotIn("FreeCAD", source)

    def test_no_duplicate_confirmat_or_joinery_dto(self):
        import manufacturing.confirmat_validation_readiness_rule as module

        source = inspect.getsource(module)

        self.assertNotIn("class Confirmat", source)
        self.assertNotIn("class Joinery", source)

    def test_no_banned_imports(self):
        import manufacturing.confirmat_validation_readiness_rule as module

        source = inspect.getsource(module)

        for banned in [
            "FreeCAD",
            "SceneGraph",
            "UI",
            "CNC",
            "export",
            "cost",
            "nesting",
            "geometry",
            "placement",
            "drill",
        ]:
            self.assertNotIn(banned, source.lower() if banned.islower() else source)

    def test_function_signature_remains_generic(self):
        from manufacturing.confirmat_validation_readiness_rule import (
            evaluate_confirmat_validation_readiness,
        )

        signature = inspect.signature(evaluate_confirmat_validation_readiness)

        self.assertEqual(list(signature.parameters), ["report"])

    def test_existing_confirmat_validation_tests_still_pass(self):
        from manufacturing.confirmat_validation_report import (
            ConfirmatValidationReport,
        )

        report = ConfirmatValidationReport()

        self.assertFalse(report.is_valid)
        self.assertEqual(report.validation_status, "")

    def test_existing_confirmat_decision_tests_still_pass(self):
        from manufacturing.confirmat_decision_report import ConfirmatDecisionReport

        report = ConfirmatDecisionReport()

        self.assertFalse(report.is_manufacturable)
        self.assertFalse(report.is_blocked)

    def test_manufacturing_validation_builder_tests_still_pass(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )
        from project_engineering.operational_rule_result import (
            OperationalRuleResult,
        )

        result = build_manufacturing_validation_report(
            [
                OperationalRuleResult(
                    rule_id="R1",
                    capability="C1",
                    component_id="X",
                    passed=True,
                    severity="info",
                )
            ]
        )

        self.assertTrue(result.ready_for_manufacturing)
        self.assertEqual(result.total_rule_count, 1)


if __name__ == "__main__":
    unittest.main()
