import unittest
from unittest.mock import patch


class TestDrawerIntelligenceBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.drawer_intelligence_builder import DrawerIntelligenceBuilder

        self.builder = DrawerIntelligenceBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_returns_drawer_intelligence_report(self):
        from manufacturing.drawer_intelligence_report import DrawerIntelligenceReport

        report = self.builder.build(self._validation_report())

        self.assertIsInstance(report, DrawerIntelligenceReport)

    def test_builder_includes_structural_report(self):
        report = self.builder.build(
            self._validation_report(
                requires_review=True,
                drawer_width_risk="HIGH",
                bottom_panel_warning="Check bottom panel",
            )
        )

        self.assertEqual(report.structural.structural_risk, "HIGH")
        self.assertEqual(report.structural.slide_capacity_risk, "HIGH")
        self.assertEqual(report.structural.bottom_panel_risk, "MEDIUM")
        self.assertTrue(report.structural.requires_reinforcement)

    @patch("manufacturing.drawer_intelligence_builder.DrawerDecisionBuilder")
    def test_builder_delegates_to_drawer_decision_builder(self, decision_builder_class):
        validation = self._validation_report(
            is_valid=True,
            manufacturing_ready=True,
        )
        decision_report = self._decision_report(decision_status="APPROVED")
        decision_builder_class.return_value.build.return_value = decision_report

        report = self.builder.build(validation)

        decision_builder_class.return_value.build.assert_called_once_with(validation)
        self.assertIs(report.decision, decision_report)

    @patch("manufacturing.drawer_intelligence_builder.DrawerDecisionBuilder")
    def test_builder_uses_drawer_decision_builder_exactly_once(self, decision_builder_class):
        validation = self._validation_report()
        decision_builder_class.return_value.build.return_value = self._decision_report()

        self.builder.build(validation)

        decision_builder_class.assert_called_once_with()
        decision_builder_class.return_value.build.assert_called_once_with(validation)

    def test_builder_preserves_validation_instance(self):
        validation = self._validation_report(
            is_valid=True,
            manufacturing_ready=True,
            blocking_issues=["issue"],
            warnings=["warning"],
        )

        report = self.builder.build(validation)

        self.assertIs(report.validation, validation)

    def test_builder_stores_returned_decision_report(self):
        validation = self._validation_report(
            is_valid=True,
            manufacturing_ready=True,
        )

        report = self.builder.build(validation)

        self.assertEqual(report.decision.decision_status, "APPROVED")
        self.assertEqual(report.decision.factory_visibility_message, "Drawer is ready for production")

    def test_builder_does_not_mutate_validation_report(self):
        validation = self._validation_report(
            is_valid=False,
            blocking_issues=["Issue A"],
            warnings=["Warning A"],
        )
        snapshot = self._snapshot(validation)

        self.builder.build(validation)

        self.assertEqual(self._snapshot(validation), snapshot)

    def test_builder_preserves_blocking_issues(self):
        validation = self._validation_report(
            is_valid=False,
            blocking_issues=["Issue A", "Issue B"],
        )

        report = self.builder.build(validation)

        self.assertEqual(validation.blocking_issues, ["Issue A", "Issue B"])
        self.assertEqual(report.validation.blocking_issues, ["Issue A", "Issue B"])

    def test_builder_preserves_warnings(self):
        validation = self._validation_report(
            is_valid=True,
            manufacturing_ready=False,
            warnings=["Warning A", "Warning B"],
        )

        report = self.builder.build(validation)

        self.assertEqual(validation.warnings, ["Warning A", "Warning B"])
        self.assertEqual(report.validation.warnings, ["Warning A", "Warning B"])

    def test_valid_approved_drawer_flows_through_intelligence_report(self):
        validation = self._validation_report(
            is_valid=True,
            manufacturing_ready=True,
            slide_installation_valid=True,
            clearance_valid=True,
            hardware_complete=True,
        )

        report = self.builder.build(validation)

        self.assertEqual(report.validation, validation)
        self.assertEqual(report.decision.decision_status, "APPROVED")
        self.assertTrue(report.decision.is_manufacturable)
        self.assertFalse(report.decision.is_blocked)
        self.assertFalse(report.decision.requires_review)

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _validation_report(
        is_valid=False,
        manufacturing_ready=False,
        slide_installation_valid=False,
        clearance_valid=False,
        hardware_complete=False,
        requires_review=False,
        drawer_width_risk="LOW",
        bottom_panel_warning="",
        blocking_issues=None,
        warnings=None,
    ):
        from manufacturing.drawer_validation_report import DrawerValidationReport

        report = DrawerValidationReport(
            is_valid=is_valid,
            manufacturing_ready=manufacturing_ready,
            slide_installation_valid=slide_installation_valid,
            clearance_valid=clearance_valid,
            hardware_complete=hardware_complete,
            blocking_issues=list(blocking_issues or []),
            warnings=list(warnings or []),
        )
        report.requires_review = requires_review
        report.drawer_width_risk = drawer_width_risk
        report.bottom_panel_warning = bottom_panel_warning
        return report

    @staticmethod
    def _decision_report(
        decision_status="APPROVED",
        is_manufacturable=True,
        is_blocked=False,
        requires_review=False,
        blocking_reason="",
        warning_reason="",
        recommended_fix="",
        factory_visibility_message="Drawer is ready for production",
    ):
        from manufacturing.drawer_decision_report import DrawerDecisionReport

        return DrawerDecisionReport(
            decision_status=decision_status,
            is_manufacturable=is_manufacturable,
            is_blocked=is_blocked,
            requires_review=requires_review,
            blocking_reason=blocking_reason,
            warning_reason=warning_reason,
            recommended_fix=recommended_fix,
            factory_visibility_message=factory_visibility_message,
        )


if __name__ == "__main__":
    unittest.main()
