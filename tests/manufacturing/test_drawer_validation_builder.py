import unittest
from dataclasses import dataclass


@dataclass
class _DrawerRulesReport:
    drawer_width: float = 500.0
    drawer_depth: float = 400.0
    slide_length: float = 350.0
    bottom_panel_thickness: float = 8.0
    hardware_complete: bool = True
    tags: list = None


class TestDrawerValidationBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.drawer_validation_builder import DrawerValidationBuilder

        self.builder = DrawerValidationBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_returns_drawer_validation_report(self):
        from manufacturing.drawer_validation_report import DrawerValidationReport

        report = self.builder.build(self._rules_report())

        self.assertIsInstance(report, DrawerValidationReport)

    def test_zero_width_blocks_validation(self):
        report = self.builder.build(self._rules_report(drawer_width=0))

        self.assertFalse(report.is_valid)
        self.assertIn("Drawer width must be greater than zero", report.blocking_issues)

    def test_zero_depth_blocks_validation(self):
        report = self.builder.build(self._rules_report(drawer_depth=0))

        self.assertFalse(report.is_valid)
        self.assertIn("Drawer depth must be greater than zero", report.blocking_issues)

    def test_wide_drawer_creates_medium_width_risk(self):
        report = self.builder.build(self._rules_report(drawer_width=800))

        self.assertEqual(report.drawer_width_risk, "MEDIUM")

    def test_deep_drawer_creates_medium_depth_risk(self):
        report = self.builder.build(self._rules_report(drawer_depth=550))

        self.assertEqual(report.drawer_depth_risk, "MEDIUM")

    def test_thin_bottom_panel_creates_warning(self):
        report = self.builder.build(
            self._rules_report(bottom_panel_thickness=5.5)
        )

        self.assertEqual(
            report.bottom_panel_warning,
            "Drawer bottom panel may be too thin",
        )

    def test_slide_longer_than_drawer_depth_invalidates_slide_installation(self):
        report = self.builder.build(
            self._rules_report(drawer_depth=400, slide_length=450)
        )

        self.assertFalse(report.slide_installation_valid)
        self.assertIn("Drawer slide installation is invalid", report.blocking_issues)

    def test_missing_hardware_blocks_validation(self):
        report = self.builder.build(self._rules_report(hardware_complete=False))

        self.assertFalse(report.is_valid)
        self.assertIn("Drawer hardware is incomplete", report.blocking_issues)

    def test_medium_risks_require_review_but_remain_valid(self):
        report = self.builder.build(
            self._rules_report(
                drawer_width=800,
                drawer_depth=550,
                slide_length=500,
            )
        )

        self.assertTrue(report.is_valid)
        self.assertFalse(report.manufacturing_ready)
        self.assertTrue(report.requires_review)

    def test_valid_drawer_is_manufacturing_ready(self):
        report = self.builder.build(self._rules_report())

        self.assertTrue(report.is_valid)
        self.assertTrue(report.manufacturing_ready)
        self.assertFalse(report.requires_review)

    def test_builder_does_not_mutate_input(self):
        rules = self._rules_report(
            drawer_width=800,
            drawer_depth=550,
            slide_length=500,
            bottom_panel_thickness=5.5,
            tags=["a", "b"],
        )
        snapshot = self._snapshot(rules)

        self.builder.build(rules)

        self.assertEqual(self._snapshot(rules), snapshot)

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _rules_report(
        drawer_width=500.0,
        drawer_depth=400.0,
        slide_length=350.0,
        bottom_panel_thickness=8.0,
        hardware_complete=True,
        tags=None,
    ):
        return _DrawerRulesReport(
            drawer_width=drawer_width,
            drawer_depth=drawer_depth,
            slide_length=slide_length,
            bottom_panel_thickness=bottom_panel_thickness,
            hardware_complete=hardware_complete,
            tags=list(tags or []),
        )


if __name__ == "__main__":
    unittest.main()
