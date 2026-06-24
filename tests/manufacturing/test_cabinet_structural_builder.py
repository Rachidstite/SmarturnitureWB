import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestCabinetStructuralBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.cabinet_structural_builder import (
            CabinetStructuralBuilder,
        )

        self.builder = CabinetStructuralBuilder()

    def test_report_contract(self):
        from manufacturing.cabinet_structural_report import (
            CabinetStructuralReport,
        )
        from manufacturing.shelf_structural_report import ShelfStructuralReport

        self.assertTrue(is_dataclass(CabinetStructuralReport))
        self.assertEqual(
            [field.name for field in fields(CabinetStructuralReport)],
            [
                "structural_risk",
                "stability_risk",
                "requires_center_support",
                "requires_reinforcement",
                "anti_racking_risk",
                "structural_recommendation",
                "shelf_structural",
            ],
        )

        report = CabinetStructuralReport()

        self.assertEqual(report.structural_risk, "LOW")
        self.assertEqual(report.stability_risk, "LOW")
        self.assertFalse(report.requires_center_support)
        self.assertFalse(report.requires_reinforcement)
        self.assertEqual(report.anti_racking_risk, "LOW")
        self.assertEqual(report.structural_recommendation, "")
        self.assertIsInstance(report.shelf_structural, ShelfStructuralReport)

    def test_high_back_panel_structural_risk_propagates(self):
        report = self.builder.build(
            self._back_panel_intelligence_report(
                decision_requires_review=True,
                structural_risk="HIGH",
            )
        )

        self.assertEqual(report.structural_risk, "HIGH")

    def test_reinforcement_propagates(self):
        report = self.builder.build(
            self._back_panel_intelligence_report(
                structural_requires_reinforcement=True,
            )
        )

        self.assertTrue(report.requires_reinforcement)

    def test_low_racking_resistance_gives_high_anti_racking_risk(self):
        report = self.builder.build(
            self._back_panel_intelligence_report(racking_resistance="LOW")
        )

        self.assertEqual(report.anti_racking_risk, "HIGH")

    def test_medium_racking_resistance_gives_medium_anti_racking_risk(self):
        report = self.builder.build(
            self._back_panel_intelligence_report(racking_resistance="MEDIUM")
        )

        self.assertEqual(report.anti_racking_risk, "MEDIUM")

    def test_drawer_review_gives_medium_stability_risk(self):
        report = self.builder.build(
            self._back_panel_intelligence_report(),
            self._drawer_intelligence_report(decision_requires_review=True),
        )

        self.assertEqual(report.stability_risk, "MEDIUM")

    def test_shelf_high_span_propagates(self):
        report = self.builder.build(
            self._back_panel_intelligence_report(),
            shelf_structural_report=self._shelf_structural_report(span_risk="HIGH"),
        )

        self.assertEqual(report.structural_risk, "HIGH")

    def test_shelf_support_propagates(self):
        report = self.builder.build(
            self._back_panel_intelligence_report(),
            shelf_structural_report=self._shelf_structural_report(
                support_required=True
            ),
        )

        self.assertTrue(report.requires_reinforcement)

    def test_shelf_sagging_affects_stability(self):
        report = self.builder.build(
            self._back_panel_intelligence_report(),
            shelf_structural_report=self._shelf_structural_report(
                sagging_risk="HIGH"
            ),
        )

        self.assertEqual(report.stability_risk, "MEDIUM")

    def test_shelf_recommendation_propagates(self):
        report = self.builder.build(
            self._back_panel_intelligence_report(),
            shelf_structural_report=self._shelf_structural_report(
                shelf_recommendation="Shelf span should be reviewed"
            ),
        )

        self.assertEqual(
            report.structural_recommendation,
            "Shelf span should be reviewed",
        )

    def test_high_risk_requires_center_support(self):
        report = self.builder.build(
            self._back_panel_intelligence_report(
                structural_risk="HIGH",
                racking_resistance="LOW",
            )
        )

        self.assertTrue(report.requires_center_support)

    def test_recommendation_propagation(self):
        report = self.builder.build(
            self._back_panel_intelligence_report(
                structural_risk="HIGH",
                racking_resistance="LOW",
            )
        )

        self.assertEqual(
            report.structural_recommendation,
            "Cabinet requires structural reinforcement review",
        )

    def test_safe_defaults(self):
        report = self.builder.build(self._back_panel_intelligence_report())

        self.assertEqual(report.structural_risk, "LOW")
        self.assertEqual(report.stability_risk, "LOW")
        self.assertFalse(report.requires_center_support)
        self.assertFalse(report.requires_reinforcement)
        self.assertEqual(report.anti_racking_risk, "LOW")
        self.assertEqual(report.structural_recommendation, "")

    def test_builder_does_not_mutate_inputs(self):
        back_panel = self._back_panel_intelligence_report(
            decision_requires_review=True,
            structural_risk="MEDIUM",
            structural_requires_reinforcement=True,
            racking_resistance="MEDIUM",
            tags=["a", "b"],
        )
        drawer = self._drawer_intelligence_report(
            decision_requires_review=True,
            tags=["x", "y"],
        )
        back_panel_snapshot = self._snapshot(back_panel)
        drawer_snapshot = self._snapshot(drawer)
        shelf = self._shelf_structural_report(
            span_risk="MEDIUM",
            support_required=True,
            tags=["shelf"],
        )
        shelf_snapshot = self._snapshot(shelf)

        self.builder.build(back_panel, drawer, shelf)

        self.assertEqual(self._snapshot(back_panel), back_panel_snapshot)
        self.assertEqual(self._snapshot(drawer), drawer_snapshot)
        self.assertEqual(self._snapshot(shelf), shelf_snapshot)

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _back_panel_intelligence_report(
        decision_requires_review=False,
        structural_risk="LOW",
        structural_requires_reinforcement=False,
        racking_resistance="UNKNOWN",
        tags=None,
    ):
        back_panel_decision = SimpleNamespace(requires_review=decision_requires_review)
        back_panel_structural = SimpleNamespace(
            structural_risk=structural_risk,
            requires_reinforcement=structural_requires_reinforcement,
            racking_resistance=racking_resistance,
        )
        report = SimpleNamespace(
            decision=back_panel_decision,
            structural=back_panel_structural,
        )
        report.tags = list(tags or [])
        return report

    @staticmethod
    def _drawer_intelligence_report(decision_requires_review=False, tags=None):
        drawer_decision = SimpleNamespace(requires_review=decision_requires_review)
        report = SimpleNamespace(decision=drawer_decision)
        report.tags = list(tags or [])
        return report

    @staticmethod
    def _shelf_structural_report(
        span_risk="LOW",
        sagging_risk="LOW",
        support_required=False,
        shelf_recommendation="",
        tags=None,
    ):
        report = SimpleNamespace(
            span_risk=span_risk,
            sagging_risk=sagging_risk,
            support_required=support_required,
            shelf_recommendation=shelf_recommendation,
        )
        report.tags = list(tags or [])
        return report


if __name__ == "__main__":
    unittest.main()
