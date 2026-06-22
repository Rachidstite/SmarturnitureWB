import unittest
from unittest.mock import patch


class TestBackPanelIntelligenceBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.back_panel_intelligence_builder import (
            BackPanelIntelligenceBuilder,
        )

        self.builder = BackPanelIntelligenceBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_returns_back_panel_intelligence_report(self):
        from manufacturing.back_panel_intelligence_report import (
            BackPanelIntelligenceReport,
        )

        report = self.builder.build(
            self._hole_rules_report(),
            self._manufacturing_intent_report(),
            self._validation_report(),
            self._commercial_risk_report(),
        )

        self.assertIsInstance(report, BackPanelIntelligenceReport)

    @patch("manufacturing.back_panel_intelligence_builder.BackPanelDecisionBuilder")
    def test_builder_delegates_to_back_panel_decision_builder(self, decision_builder_class):
        validation = self._validation_report(
            is_valid=True,
        )
        decision_report = self._decision_report(decision_status="APPROVED")
        decision_builder_class.return_value.build.return_value = decision_report

        report = self.builder.build(
            self._hole_rules_report(),
            self._manufacturing_intent_report(),
            validation,
            self._commercial_risk_report(),
        )

        decision_builder_class.return_value.build.assert_called_once_with(validation)
        self.assertIs(report.decision, decision_report)

    @patch("manufacturing.back_panel_intelligence_builder.BackPanelDecisionBuilder")
    def test_builder_uses_back_panel_decision_builder_exactly_once(self, decision_builder_class):
        validation = self._validation_report()
        decision_builder_class.return_value.build.return_value = self._decision_report()

        self.builder.build(
            self._hole_rules_report(),
            self._manufacturing_intent_report(),
            validation,
            self._commercial_risk_report(),
        )

        decision_builder_class.assert_called_once_with()
        decision_builder_class.return_value.build.assert_called_once_with(validation)

    def test_builder_preserves_hole_rules_instance(self):
        hole_rules = self._hole_rules_report()
        report = self.builder.build(
            hole_rules,
            self._manufacturing_intent_report(),
            self._validation_report(),
            self._commercial_risk_report(),
        )

        self.assertIs(report.hole_rules, hole_rules)

    def test_builder_preserves_manufacturing_intent_instance(self):
        manufacturing_intent = self._manufacturing_intent_report()
        report = self.builder.build(
            self._hole_rules_report(),
            manufacturing_intent,
            self._validation_report(),
            self._commercial_risk_report(),
        )

        self.assertIs(report.manufacturing_intent, manufacturing_intent)

    def test_builder_preserves_validation_instance(self):
        validation = self._validation_report()
        report = self.builder.build(
            self._hole_rules_report(),
            self._manufacturing_intent_report(),
            validation,
            self._commercial_risk_report(),
        )

        self.assertIs(report.validation, validation)

    def test_builder_preserves_commercial_risk_instance(self):
        commercial_risk = self._commercial_risk_report()
        report = self.builder.build(
            self._hole_rules_report(),
            self._manufacturing_intent_report(),
            self._validation_report(),
            commercial_risk,
        )

        self.assertIs(report.commercial_risk, commercial_risk)

    def test_builder_stores_returned_decision_report(self):
        validation = self._validation_report(is_valid=True)

        report = self.builder.build(
            self._hole_rules_report(),
            self._manufacturing_intent_report(),
            validation,
            self._commercial_risk_report(),
        )

        self.assertEqual(report.decision.decision_status, "APPROVED")
        self.assertEqual(report.decision.factory_visibility_message, "Back panel is ready for production")

    def test_builder_does_not_mutate_inputs(self):
        hole_rules = self._hole_rules_report()
        manufacturing_intent = self._manufacturing_intent_report()
        validation = self._validation_report(
            is_valid=False,
            recommended_action="Check back panel design",
            blocking_issues=["Issue A"],
            warnings=["Warning A"],
        )
        commercial_risk = self._commercial_risk_report()

        snapshots = [
            self._snapshot(hole_rules),
            self._snapshot(manufacturing_intent),
            self._snapshot(validation),
            self._snapshot(commercial_risk),
        ]

        self.builder.build(
            hole_rules,
            manufacturing_intent,
            validation,
            commercial_risk,
        )

        self.assertEqual(
            [
                self._snapshot(hole_rules),
                self._snapshot(manufacturing_intent),
                self._snapshot(validation),
                self._snapshot(commercial_risk),
            ],
            snapshots,
        )

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _hole_rules_report():
        from manufacturing.back_panel_hole_rule_report import BackPanelHoleRuleReport

        return BackPanelHoleRuleReport(
            minimum_panel_width=100.0,
            minimum_panel_height=200.0,
            spacing_rule="STANDARD",
            edge_rule="EDGE",
            corner_rule="CORNER",
            maximum_spacing=32.0,
            requires_center_holes=False,
        )

    @staticmethod
    def _manufacturing_intent_report():
        from manufacturing.back_panel_manufacturing_intent_report import (
            BackPanelManufacturingIntentReport,
        )

        return BackPanelManufacturingIntentReport(
            fixing_intent="FIX",
            assembly_intent="ASSEMBLY",
            manufacturing_intent="MANUFACTURE",
            requires_groove=True,
            requires_fasteners=True,
            requires_center_support=False,
            fastener_type="SCREW",
            back_panel_method="STANDARD",
            cnc_preparation_required=True,
            visual_manufacturing_intent_required=False,
        )

    @staticmethod
    def _validation_report(
        is_valid=False,
        validation_status="",
        width_risk="",
        height_risk="",
        spacing_risk="",
        edge_risk="",
        corner_risk="",
        center_support_required=False,
        center_holes_required=False,
        fixing_method_warning="",
        manufacturing_warning="",
        recommended_action="",
        blocking_issues=None,
        warnings=None,
    ):
        from manufacturing.back_panel_validation_report import (
            BackPanelValidationReport,
        )

        return BackPanelValidationReport(
            is_valid=is_valid,
            validation_status=validation_status,
            width_risk=width_risk,
            height_risk=height_risk,
            spacing_risk=spacing_risk,
            edge_risk=edge_risk,
            corner_risk=corner_risk,
            center_support_required=center_support_required,
            center_holes_required=center_holes_required,
            fixing_method_warning=fixing_method_warning,
            manufacturing_warning=manufacturing_warning,
            recommended_action=recommended_action,
        )

    @staticmethod
    def _commercial_risk_report():
        from manufacturing.back_panel_commercial_risk_report import (
            BackPanelCommercialRiskReport,
        )

        return BackPanelCommercialRiskReport(
            risk_level="LOW",
            rework_risk="LOW",
            scrap_risk="LOW",
            labor_delay_risk="LOW",
            cnc_error_risk="LOW",
            customer_complaint_risk="LOW",
            profitability_impact="LOW",
            estimated_waste_category="LOW",
            commercial_warning="",
            recommended_commercial_action="",
        )

    @staticmethod
    def _decision_report(
        decision_status="APPROVED",
        is_manufacturable=True,
        is_blocked=False,
        requires_review=False,
        blocking_reason="",
        warning_reason="",
        recommended_fix="",
        manufacturing_priority="LOW",
        factory_visibility_message="Back panel is ready for production",
    ):
        from manufacturing.back_panel_decision_report import (
            BackPanelDecisionReport,
        )

        return BackPanelDecisionReport(
            decision_status=decision_status,
            is_manufacturable=is_manufacturable,
            is_blocked=is_blocked,
            requires_review=requires_review,
            blocking_reason=blocking_reason,
            warning_reason=warning_reason,
            recommended_fix=recommended_fix,
            manufacturing_priority=manufacturing_priority,
            factory_visibility_message=factory_visibility_message,
        )


if __name__ == "__main__":
    unittest.main()
