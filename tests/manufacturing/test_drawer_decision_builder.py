import unittest


class TestDrawerDecisionBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.drawer_decision_builder import DrawerDecisionBuilder

        self.builder = DrawerDecisionBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_returns_drawer_decision_report(self):
        from manufacturing.drawer_decision_report import DrawerDecisionReport

        report = self.builder.build(self._validation_report())

        self.assertIsInstance(report, DrawerDecisionReport)

    def test_invalid_validation_blocks_production(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=False,
                manufacturing_ready=True,
            )
        )

        self.assertEqual(report.decision_status, "BLOCKED")
        self.assertFalse(report.is_manufacturable)
        self.assertTrue(report.is_blocked)
        self.assertFalse(report.requires_review)
        self.assertEqual(report.recommended_fix, "Review drawer manufacturability before production")
        self.assertEqual(report.factory_visibility_message, "Drawer is blocked for production")

    def test_invalid_validation_uses_first_blocking_issue(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=False,
                blocking_issues=["Clearance too tight", "Slide mismatch"],
            )
        )

        self.assertEqual(report.blocking_reason, "Clearance too tight")

    def test_invalid_validation_uses_fallback_blocking_reason(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=False,
                blocking_issues=[],
            )
        )

        self.assertEqual(report.blocking_reason, "Drawer validation failed")

    def test_manufacturing_ready_false_requires_review(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=True,
                manufacturing_ready=False,
                warnings=["Readiness gap"],
            )
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")
        self.assertFalse(report.is_manufacturable)
        self.assertFalse(report.is_blocked)
        self.assertTrue(report.requires_review)
        self.assertEqual(report.warning_reason, "Readiness gap")
        self.assertEqual(report.recommended_fix, "Review drawer manufacturing readiness")
        self.assertEqual(report.factory_visibility_message, "Drawer requires manufacturing review")

    def test_warnings_require_review(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=True,
                manufacturing_ready=True,
                warnings=["Check slide clearance"],
            )
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")
        self.assertTrue(report.is_manufacturable)
        self.assertFalse(report.is_blocked)
        self.assertTrue(report.requires_review)
        self.assertEqual(report.warning_reason, "Check slide clearance")
        self.assertEqual(report.recommended_fix, "Review drawer warnings before production")
        self.assertEqual(report.factory_visibility_message, "Drawer is manufacturable with warnings")

    def test_valid_ready_drawer_is_approved(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=True,
                manufacturing_ready=True,
                slide_installation_valid=True,
                clearance_valid=True,
                hardware_complete=True,
            )
        )

        self.assertEqual(report.decision_status, "APPROVED")
        self.assertTrue(report.is_manufacturable)
        self.assertFalse(report.is_blocked)
        self.assertFalse(report.requires_review)
        self.assertEqual(report.blocking_reason, "")
        self.assertEqual(report.warning_reason, "")
        self.assertEqual(report.recommended_fix, "")
        self.assertEqual(report.factory_visibility_message, "Drawer is ready for production")

    def test_builder_does_not_mutate_validation_input(self):
        validation = self._validation_report(
            is_valid=False,
            blocking_issues=["Clearance too tight"],
            warnings=["Review slide fit"],
        )
        snapshot = self._snapshot(validation)

        self.builder.build(validation)

        self.assertEqual(self._snapshot(validation), snapshot)

    def test_empty_warning_and_blocking_lists_are_safe(self):
        report = self.builder.build(
            self._validation_report(
                is_valid=False,
                blocking_issues=[],
                warnings=[],
            )
        )

        self.assertEqual(report.blocking_reason, "Drawer validation failed")
        self.assertEqual(report.warning_reason, "")

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
        blocking_issues=None,
        warnings=None,
    ):
        from manufacturing.drawer_validation_report import DrawerValidationReport

        return DrawerValidationReport(
            is_valid=is_valid,
            manufacturing_ready=manufacturing_ready,
            slide_installation_valid=slide_installation_valid,
            clearance_valid=clearance_valid,
            hardware_complete=hardware_complete,
            blocking_issues=list(blocking_issues or []),
            warnings=list(warnings or []),
        )


if __name__ == "__main__":
    unittest.main()
