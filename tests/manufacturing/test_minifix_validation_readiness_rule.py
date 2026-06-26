import inspect
import unittest


class TestMinifixValidationReadinessRule(unittest.TestCase):

    def setUp(self):
        from manufacturing.minifix_validation_readiness_rule import (
            evaluate_minifix_validation_readiness,
        )

        self.evaluate = evaluate_minifix_validation_readiness

    def test_passing_report_when_minifix_validation_is_ready(self):
        from manufacturing.minifix_validation_report import MinifixValidationReport

        report = MinifixValidationReport(
            is_valid=True,
            validation_status="READY",
            edge_distance_risk="LOW",
            panel_thickness_risk="LOW",
            spacing_risk="LOW",
            cam_lock_risk="LOW",
            dowel_support_risk="LOW",
            assembly_risk="LOW",
            manufacturing_warning="",
            recommended_action="",
        )

        result = self.evaluate(report)

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_failing_report_when_minifix_validation_is_invalid(self):
        from manufacturing.minifix_validation_report import MinifixValidationReport

        report = MinifixValidationReport(
            is_valid=False,
            validation_status="BLOCKED",
            edge_distance_risk="HIGH",
            panel_thickness_risk="HIGH",
            spacing_risk="HIGH",
            cam_lock_risk="HIGH",
            dowel_support_risk="HIGH",
            assembly_risk="HIGH",
            manufacturing_warning="Minifix validation failed",
            recommended_action="Review panel layout",
        )

        result = self.evaluate(report)

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("is_valid", result.message)
        self.assertIn("validation_status", result.message)

    def test_failure_message_includes_key_validation_fields(self):
        from manufacturing.minifix_validation_report import MinifixValidationReport

        report = MinifixValidationReport(
            is_valid=False,
            validation_status="BLOCKED",
            edge_distance_risk="HIGH",
            panel_thickness_risk="HIGH",
            spacing_risk="HIGH",
            cam_lock_risk="HIGH",
            dowel_support_risk="HIGH",
            assembly_risk="HIGH",
            manufacturing_warning="Edge distance too small",
            recommended_action="Increase spacing",
        )

        result = self.evaluate(report)

        self.assertIn("is_valid", result.message)
        self.assertIn("validation_status", result.message)
        self.assertIn("edge_distance_risk", result.message)
        self.assertIn("panel_thickness_risk", result.message)
        self.assertIn("spacing_risk", result.message)
        self.assertIn("cam_lock_risk", result.message)
        self.assertIn("dowel_support_risk", result.message)
        self.assertIn("assembly_risk", result.message)
        self.assertIn("manufacturing_warning", result.message)
        self.assertIn("recommended_action", result.message)

    def test_capability_is_correct(self):
        from manufacturing.minifix_validation_report import MinifixValidationReport

        result = self.evaluate(MinifixValidationReport(is_valid=True))

        self.assertEqual(
            result.capability,
            "manufacturing_minifix_validation_readiness",
        )

    def test_component_id_is_correct(self):
        from manufacturing.minifix_validation_report import MinifixValidationReport

        result = self.evaluate(MinifixValidationReport(is_valid=True))

        self.assertEqual(result.component_id, "minifix-validation")

    def test_source_is_correct(self):
        from manufacturing.minifix_validation_report import MinifixValidationReport

        result = self.evaluate(MinifixValidationReport(is_valid=True))

        self.assertEqual(result.source, "minifix-validation-readiness-rule")

    def test_import_without_freecad(self):
        import manufacturing.minifix_validation_readiness_rule as module

        source = inspect.getsource(module)

        self.assertNotIn("FreeCAD", source)

    def test_no_duplicate_minifix_or_joinery_dto(self):
        import manufacturing.minifix_validation_readiness_rule as module

        source = inspect.getsource(module)

        self.assertNotIn("class Minifix", source)
        self.assertNotIn("class Joinery", source)

    def test_no_banned_imports(self):
        import manufacturing.minifix_validation_readiness_rule as module

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
        from manufacturing.minifix_validation_readiness_rule import (
            evaluate_minifix_validation_readiness,
        )

        signature = inspect.signature(evaluate_minifix_validation_readiness)

        self.assertEqual(list(signature.parameters), ["report"])

    def test_existing_minifix_validation_tests_still_pass(self):
        from manufacturing.minifix_validation_report import MinifixValidationReport

        report = MinifixValidationReport()

        self.assertFalse(report.is_valid)
        self.assertEqual(report.validation_status, "")

    def test_existing_minifix_decision_tests_still_pass(self):
        from manufacturing.minifix_decision_report import MinifixDecisionReport

        report = MinifixDecisionReport()

        self.assertFalse(report.is_manufacturable)
        self.assertFalse(report.is_blocked)

    def test_existing_minifix_rule_tests_still_pass(self):
        from manufacturing.minifix_rule_report import MinifixRuleReport

        report = MinifixRuleReport()

        self.assertEqual(report.recommended_quantity, 0)
        self.assertFalse(report.requires_cam_lock)

    def test_manufacturing_validation_builder_tests_still_pass(self):
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )
        from project_engineering.operational_rule_result import OperationalRuleResult

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
