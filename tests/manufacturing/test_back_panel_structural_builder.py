import unittest


class TestBackPanelStructuralBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.back_panel_structural_builder import (
            BackPanelStructuralBuilder,
        )

        self.builder = BackPanelStructuralBuilder()

    def test_report_contract(self):
        from dataclasses import fields, is_dataclass

        from manufacturing.back_panel_structural_report import (
            BackPanelStructuralReport,
        )

        self.assertTrue(is_dataclass(BackPanelStructuralReport))
        self.assertEqual(
            [field.name for field in fields(BackPanelStructuralReport)],
            [
                "structural_risk",
                "racking_resistance",
                "requires_center_support",
                "requires_reinforcement",
                "structural_recommendation",
            ],
        )

        report = BackPanelStructuralReport()

        self.assertEqual(report.structural_risk, "LOW")
        self.assertEqual(report.racking_resistance, "UNKNOWN")
        self.assertFalse(report.requires_center_support)
        self.assertFalse(report.requires_reinforcement)
        self.assertEqual(report.structural_recommendation, "")

    def test_groove_resistance(self):
        report = self.builder.build(
            self._validation_report(center_support_required=False),
            self._fixing_report(strategy="GROOVE"),
        )

        self.assertEqual(report.racking_resistance, "HIGH")

    def test_screwed_resistance(self):
        report = self.builder.build(
            self._validation_report(center_support_required=False),
            self._fixing_report(strategy="SCREWED"),
        )

        self.assertEqual(report.racking_resistance, "MEDIUM")

    def test_stapled_resistance(self):
        report = self.builder.build(
            self._validation_report(center_support_required=False),
            self._fixing_report(strategy="STAPLED"),
        )

        self.assertEqual(report.racking_resistance, "LOW")

    def test_center_support_triggers_high_risk(self):
        report = self.builder.build(
            self._validation_report(center_support_required=True),
            self._fixing_report(strategy="GROOVE"),
        )

        self.assertEqual(report.structural_risk, "HIGH")
        self.assertEqual(
            report.structural_recommendation,
            "Consider center support for large cabinet",
        )

    def test_stapled_center_support_triggers_high_risk(self):
        report = self.builder.build(
            self._validation_report(center_support_required=True),
            self._fixing_report(strategy="STAPLED"),
        )

        self.assertEqual(report.structural_risk, "HIGH")

    def test_stapled_center_support_requires_reinforcement(self):
        report = self.builder.build(
            self._validation_report(center_support_required=True),
            self._fixing_report(strategy="STAPLED"),
        )

        self.assertTrue(report.requires_reinforcement)

    def test_stapled_center_support_replacement_recommendation(self):
        report = self.builder.build(
            self._validation_report(center_support_required=True),
            self._fixing_report(strategy="STAPLED"),
        )

        self.assertEqual(
            report.structural_recommendation,
            "Replace stapled fixing or add reinforcement",
        )

    def test_groove_center_support_recommendation_only(self):
        report = self.builder.build(
            self._validation_report(center_support_required=True),
            self._fixing_report(strategy="GROOVE"),
        )

        self.assertEqual(
            report.structural_recommendation,
            "Consider center support for large cabinet",
        )

    def test_groove_without_center_support_remains_low_risk(self):
        report = self.builder.build(
            self._validation_report(center_support_required=False),
            self._fixing_report(strategy="GROOVE"),
        )

        self.assertEqual(report.structural_risk, "LOW")

    def test_reinforcement_propagation(self):
        report = self.builder.build(
            self._validation_report(center_support_required=True),
            self._fixing_report(strategy="SCREWED"),
        )

        self.assertTrue(report.requires_reinforcement)
        self.assertTrue(report.requires_center_support)

    def test_safe_defaults(self):
        report = self.builder.build(
            self._validation_report(center_support_required=False),
            self._fixing_report(strategy="GROOVE"),
        )

        self.assertEqual(report.structural_risk, "LOW")
        self.assertFalse(report.requires_center_support)
        self.assertFalse(report.requires_reinforcement)
        self.assertEqual(report.structural_recommendation, "")

    def test_builder_does_not_mutate_inputs(self):
        validation_report = self._validation_report(
            center_support_required=True,
            tags=["a", "b"],
        )
        fixing_report = self._fixing_report(
            strategy="SCREWED",
            notes={"flag": True},
        )
        validation_snapshot = self._snapshot(validation_report)
        fixing_snapshot = self._snapshot(fixing_report)

        self.builder.build(validation_report, fixing_report)

        self.assertEqual(self._snapshot(validation_report), validation_snapshot)
        self.assertEqual(self._snapshot(fixing_report), fixing_snapshot)

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else dict(value)
            if isinstance(value, dict)
            else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _validation_report(center_support_required=False, tags=None):
        from manufacturing.back_panel_validation_report import (
            BackPanelValidationReport,
        )

        report = BackPanelValidationReport(
            center_support_required=center_support_required,
        )
        report.tags = list(tags or [])
        return report

    @staticmethod
    def _fixing_report(strategy="GROOVE", notes=None):
        from manufacturing.back_panel_fixing_report import BackPanelFixingReport
        from manufacturing.back_panel_fixing_strategy import (
            BackPanelFixingStrategy,
        )

        report = BackPanelFixingReport(
            strategy=getattr(BackPanelFixingStrategy, strategy),
        )
        report.notes = dict(notes or {})
        return report


if __name__ == "__main__":
    unittest.main()
