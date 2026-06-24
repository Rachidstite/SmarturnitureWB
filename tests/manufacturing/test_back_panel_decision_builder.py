import unittest


class TestBackPanelDecisionBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.back_panel_decision_builder import (
            BackPanelDecisionBuilder,
        )

        self.builder = BackPanelDecisionBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_returns_back_panel_decision_report(self):
        from manufacturing.back_panel_decision_report import (
            BackPanelDecisionReport,
        )

        report = self.builder.build(self._validation_report())

        self.assertIsInstance(report, BackPanelDecisionReport)

    def test_invalid_validation_blocks_production(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=False,
                recommended_action="Check back panel design",
                manufacturing_warning="Manufacturing warning",
                fixing_method_warning="Fixing warning",
            )
        )

        self.assertEqual(report.decision_status, "BLOCKED")
        self.assertFalse(report.is_manufacturable)
        self.assertTrue(report.is_blocked)
        self.assertFalse(report.requires_review)
        self.assertEqual(report.blocking_reason, "Check back panel design")
        self.assertEqual(report.warning_reason, "Manufacturing warning")
        self.assertEqual(report.recommended_fix, "Check back panel design")
        self.assertEqual(report.manufacturing_priority, "HIGH")
        self.assertEqual(report.factory_visibility_message, "Back panel is blocked for production")

    def test_invalid_validation_uses_fallback_blocking_reason(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=False,
                recommended_action="",
                manufacturing_warning="",
                fixing_method_warning="",
            )
        )

        self.assertEqual(report.blocking_reason, "Back panel validation failed")
        self.assertEqual(
            report.recommended_fix,
            "Review back panel manufacturability before production",
        )

    def test_invalid_validation_uses_recommended_action_when_present(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=False,
                recommended_action="Use center support",
            )
        )

        self.assertEqual(report.blocking_reason, "Use center support")
        self.assertEqual(report.recommended_fix, "Use center support")

    def test_center_support_requires_review(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=True,
                center_support_required=True,
                recommended_action="Add center support",
            )
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")
        self.assertTrue(report.is_manufacturable)
        self.assertFalse(report.is_blocked)
        self.assertTrue(report.requires_review)
        self.assertEqual(report.warning_reason, "Back panel requires center support")
        self.assertEqual(report.recommended_fix, "Add center support")
        self.assertEqual(report.manufacturing_priority, "MEDIUM")
        self.assertEqual(report.factory_visibility_message, "Back panel requires manufacturing review")

    def test_center_holes_require_review(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=True,
                center_holes_required=True,
                recommended_action="Add center holes",
            )
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")
        self.assertTrue(report.is_manufacturable)
        self.assertFalse(report.is_blocked)
        self.assertTrue(report.requires_review)
        self.assertEqual(report.warning_reason, "Back panel requires center fixing holes")
        self.assertEqual(report.recommended_fix, "Add center holes")
        self.assertEqual(report.manufacturing_priority, "MEDIUM")
        self.assertEqual(report.factory_visibility_message, "Back panel requires manufacturing review")

    def test_fixing_method_warning_requires_review(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=True,
                fixing_method_warning="Use different fixing method",
                recommended_action="Review fixing method",
            )
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")
        self.assertTrue(report.is_manufacturable)
        self.assertFalse(report.is_blocked)
        self.assertTrue(report.requires_review)
        self.assertEqual(report.warning_reason, "Use different fixing method")
        self.assertEqual(report.recommended_fix, "Review fixing method")
        self.assertEqual(report.manufacturing_priority, "MEDIUM")
        self.assertEqual(report.factory_visibility_message, "Back panel requires manufacturing review")

    def test_manufacturing_warning_requires_review(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=True,
                manufacturing_warning="Manufacturing warning",
                recommended_action="Review manufacturing warning",
            )
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")
        self.assertTrue(report.is_manufacturable)
        self.assertFalse(report.is_blocked)
        self.assertTrue(report.requires_review)
        self.assertEqual(report.warning_reason, "Manufacturing warning")
        self.assertEqual(report.recommended_fix, "Review manufacturing warning")
        self.assertEqual(report.manufacturing_priority, "MEDIUM")
        self.assertEqual(report.factory_visibility_message, "Back panel requires manufacturing review")

    def test_high_structural_risk_triggers_review(self):
        report = self.builder.build(
            self._validation_report(is_valid=True),
            self._structural_report(structural_risk="HIGH"),
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")
        self.assertTrue(report.requires_review)

    def test_reinforcement_triggers_review(self):
        report = self.builder.build(
            self._validation_report(is_valid=True),
            self._structural_report(requires_reinforcement=True),
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")
        self.assertTrue(report.requires_review)

    def test_structural_recommendation_propagates(self):
        report = self.builder.build(
            self._validation_report(is_valid=True),
            self._structural_report(
                structural_risk="HIGH",
                structural_recommendation="Add center support or reinforcement",
            ),
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")
        self.assertEqual(
            report.recommended_fix,
            "Add center support or reinforcement",
        )

    def test_blocked_precedence_is_preserved_with_structural_risk(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=False,
                recommended_action="Check back panel design",
            ),
            self._structural_report(structural_risk="HIGH"),
        )

        self.assertEqual(report.decision_status, "BLOCKED")
        self.assertFalse(report.requires_review)

    def test_valid_ready_back_panel_is_approved(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=True,
                center_support_required=False,
                center_holes_required=False,
                fixing_method_warning="",
                manufacturing_warning="",
            )
        )

        self.assertEqual(report.decision_status, "APPROVED")
        self.assertTrue(report.is_manufacturable)
        self.assertFalse(report.is_blocked)
        self.assertFalse(report.requires_review)
        self.assertEqual(report.blocking_reason, "")
        self.assertEqual(report.warning_reason, "")
        self.assertEqual(report.recommended_fix, "")
        self.assertEqual(report.manufacturing_priority, "LOW")
        self.assertEqual(report.factory_visibility_message, "Back panel is ready for production")

    def test_builder_does_not_mutate_validation_input(self):
        validation = self._validation_report(
            is_valid=False,
            recommended_action="Check back panel design",
            blocking_issues=["Panel issue"],
            warnings=["Panel warning"],
        )
        snapshot = self._snapshot(validation)

        self.builder.build(validation)

        self.assertEqual(self._snapshot(validation), snapshot)

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

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
    def _structural_report(
        structural_risk="LOW",
        racking_resistance="UNKNOWN",
        requires_center_support=False,
        requires_reinforcement=False,
        structural_recommendation="",
    ):
        from manufacturing.back_panel_structural_report import (
            BackPanelStructuralReport,
        )

        return BackPanelStructuralReport(
            structural_risk=structural_risk,
            racking_resistance=racking_resistance,
            requires_center_support=requires_center_support,
            requires_reinforcement=requires_reinforcement,
            structural_recommendation=structural_recommendation,
        )


if __name__ == "__main__":
    unittest.main()
