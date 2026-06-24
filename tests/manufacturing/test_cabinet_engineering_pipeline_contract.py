import unittest
from types import SimpleNamespace


class TestCabinetEngineeringPipelineContract(unittest.TestCase):

    def setUp(self):
        from manufacturing.cabinet_engineering_builder import (
            CabinetEngineeringBuilder,
        )
        from manufacturing.cabinet_structural_builder import (
            CabinetStructuralBuilder,
        )
        from manufacturing.cabinet_stability_builder import (
            CabinetStabilityBuilder,
        )

        self.engineering_builder = CabinetEngineeringBuilder()
        self.structural_builder = CabinetStructuralBuilder()
        self.stability_builder = CabinetStabilityBuilder()

    def test_engineering_builder_produces_dimensional_risk(self):
        report = self.engineering_builder.build(
            cabinet_height=2200,
            cabinet_width=1200,
        )

        self.assertEqual(report.cabinet_height_risk, "HIGH")
        self.assertEqual(report.cabinet_width_risk, "HIGH")
        self.assertTrue(report.center_divider_required)
        self.assertTrue(report.wall_anchoring_recommended)
        self.assertTrue(report.shelf_support_recommended)
        self.assertEqual(
            report.engineering_recommendation,
            "Cabinet engineering review required",
        )

    def test_structural_builder_consumes_shelf_structural_report(self):
        back_panel_report = self._back_panel_intelligence_report()
        shelf_structural_report = self._shelf_structural_report(
            span_risk="HIGH",
            sagging_risk="HIGH",
            support_required=True,
        )
        before_snapshot = self._snapshot(
            back_panel_report,
            shelf_structural_report,
        )

        report = self.structural_builder.build(
            back_panel_report,
            shelf_structural_report=shelf_structural_report,
        )

        self.assertEqual(report.structural_risk, "HIGH")
        self.assertTrue(report.requires_reinforcement)
        self.assertTrue(report.requires_center_support)
        self.assertEqual(report.stability_risk, "MEDIUM")
        self.assertEqual(
            report.structural_recommendation,
            "Cabinet requires structural reinforcement review",
        )
        self.assertEqual(
            self._snapshot(back_panel_report, shelf_structural_report),
            before_snapshot,
        )

    def test_stability_builder_consumes_structural_report_and_dimensions(self):
        structural_report = self.structural_builder.build(
            self._back_panel_intelligence_report(
                structural_risk="HIGH",
                structural_requires_reinforcement=True,
                racking_resistance="LOW",
            ),
            shelf_structural_report=self._shelf_structural_report(
                span_risk="HIGH",
                support_required=True,
            ),
        )
        before_snapshot = self._snapshot(structural_report)

        report = self.stability_builder.build(
            structural_report,
            cabinet_height=2200,
            cabinet_width=1200,
        )

        self.assertEqual(report.tipping_risk, "HIGH")
        self.assertEqual(report.large_span_risk, "HIGH")
        self.assertTrue(report.wall_anchoring_required)
        self.assertEqual(
            report.stability_recommendation,
            "Cabinet should be anchored and structurally reviewed",
        )
        self.assertEqual(self._snapshot(structural_report), before_snapshot)

    def test_tall_wide_high_risk_chain_is_coherent_and_inputs_are_not_mutated(self):
        back_panel_report = self._back_panel_intelligence_report(
            decision_requires_review=True,
            structural_risk="HIGH",
            structural_requires_reinforcement=True,
            racking_resistance="LOW",
            tags=["back"],
        )
        shelf_structural_report = self._shelf_structural_report(
            span_risk="HIGH",
            sagging_risk="HIGH",
            support_required=True,
            shelf_recommendation="Shelf support recommended",
            tags=["shelf"],
        )
        back_panel_snapshot = self._snapshot(back_panel_report)
        shelf_snapshot = self._snapshot(shelf_structural_report)

        engineering_report = self.engineering_builder.build(
            cabinet_height=2200,
            cabinet_width=1200,
        )
        structural_report = self.structural_builder.build(
            back_panel_report,
            shelf_structural_report=shelf_structural_report,
        )
        stability_report = self.stability_builder.build(
            structural_report,
            cabinet_height=2200,
            cabinet_width=1200,
        )

        self.assertEqual(engineering_report.engineering_recommendation, "Cabinet engineering review required")
        self.assertTrue(structural_report.requires_reinforcement)
        self.assertEqual(structural_report.structural_risk, "HIGH")
        self.assertTrue(stability_report.wall_anchoring_required)
        self.assertEqual(stability_report.tipping_risk, "HIGH")
        self.assertEqual(stability_report.large_span_risk, "HIGH")
        self.assertEqual(
            self._snapshot(back_panel_report),
            back_panel_snapshot,
        )
        self.assertEqual(
            self._snapshot(shelf_structural_report),
            shelf_snapshot,
        )

    @staticmethod
    def _snapshot(*items):
        def freeze(value):
            if isinstance(value, list):
                return [freeze(item) for item in value]
            if isinstance(value, dict):
                return {key: freeze(item) for key, item in value.items()}
            if hasattr(value, "__dict__"):
                return {
                    key: freeze(item)
                    for key, item in value.__dict__.items()
                }
            return value

        return [freeze(item) for item in items]

    @staticmethod
    def _back_panel_intelligence_report(
        decision_requires_review=False,
        structural_risk="LOW",
        structural_requires_reinforcement=False,
        racking_resistance="LOW",
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
