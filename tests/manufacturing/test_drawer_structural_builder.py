import unittest


class TestDrawerStructuralBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.drawer_structural_builder import DrawerStructuralBuilder

        self.builder = DrawerStructuralBuilder()

    def test_report_contract(self):
        from dataclasses import fields, is_dataclass

        from manufacturing.drawer_structural_report import DrawerStructuralReport

        self.assertTrue(is_dataclass(DrawerStructuralReport))
        self.assertEqual(
            [field.name for field in fields(DrawerStructuralReport)],
            [
                "structural_risk",
                "slide_capacity_risk",
                "bottom_panel_risk",
                "requires_reinforcement",
                "structural_recommendation",
            ],
        )

        report = DrawerStructuralReport()

        self.assertEqual(report.structural_risk, "LOW")
        self.assertEqual(report.slide_capacity_risk, "LOW")
        self.assertEqual(report.bottom_panel_risk, "LOW")
        self.assertFalse(report.requires_reinforcement)
        self.assertEqual(report.structural_recommendation, "")

    def test_high_review_means_high_structural_risk(self):
        report = self.builder.build(self._validation_report(requires_review=True))

        self.assertEqual(report.structural_risk, "HIGH")

    def test_reinforcement_propagation(self):
        report = self.builder.build(self._validation_report(requires_review=True))

        self.assertTrue(report.requires_reinforcement)

    def test_width_risk_sets_slide_capacity_risk(self):
        report = self.builder.build(
            self._validation_report(requires_review=False, drawer_width_risk="HIGH")
        )

        self.assertEqual(report.slide_capacity_risk, "HIGH")

    def test_bottom_panel_warning_sets_medium_risk(self):
        report = self.builder.build(
            self._validation_report(bottom_panel_warning="Check bottom panel")
        )

        self.assertEqual(report.bottom_panel_risk, "MEDIUM")

    def test_recommendation_propagation(self):
        report = self.builder.build(self._validation_report(requires_review=True))

        self.assertEqual(
            report.structural_recommendation,
            "Review drawer structure and slide capacity",
        )

    def test_safe_defaults(self):
        report = self.builder.build(self._validation_report())

        self.assertEqual(report.structural_risk, "LOW")
        self.assertEqual(report.slide_capacity_risk, "LOW")
        self.assertEqual(report.bottom_panel_risk, "LOW")
        self.assertFalse(report.requires_reinforcement)
        self.assertEqual(report.structural_recommendation, "")

    def test_builder_does_not_mutate_inputs(self):
        validation = self._validation_report(
            requires_review=True,
            drawer_width_risk="HIGH",
            bottom_panel_warning="Check bottom panel",
            tags=["a", "b"],
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
        requires_review=False,
        drawer_width_risk="LOW",
        bottom_panel_warning="",
        tags=None,
    ):
        from manufacturing.drawer_validation_report import DrawerValidationReport

        report = DrawerValidationReport(
            is_valid=True,
            manufacturing_ready=True,
            slide_installation_valid=True,
            clearance_valid=True,
            hardware_complete=True,
        )
        report.requires_review = requires_review
        report.drawer_width_risk = drawer_width_risk
        report.bottom_panel_warning = bottom_panel_warning
        report.tags = list(tags or [])
        return report


if __name__ == "__main__":
    unittest.main()
