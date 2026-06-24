import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestCabinetStabilityBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.cabinet_stability_builder import CabinetStabilityBuilder

        self.builder = CabinetStabilityBuilder()

    def test_report_contract(self):
        from manufacturing.cabinet_stability_report import CabinetStabilityReport

        self.assertTrue(is_dataclass(CabinetStabilityReport))
        self.assertEqual(
            [field.name for field in fields(CabinetStabilityReport)],
            [
                "tipping_risk",
                "wall_anchoring_required",
                "large_span_risk",
                "stability_recommendation",
            ],
        )

        report = CabinetStabilityReport()

        self.assertEqual(report.tipping_risk, "LOW")
        self.assertFalse(report.wall_anchoring_required)
        self.assertEqual(report.large_span_risk, "LOW")
        self.assertEqual(report.stability_recommendation, "")

    def test_tall_cabinet_creates_medium_tipping_risk(self):
        report = self.builder.build(self._structural_report(), cabinet_height=1800)

        self.assertEqual(report.tipping_risk, "MEDIUM")

    def test_tall_cabinet_and_high_structural_risk_creates_high_tipping_risk(self):
        report = self.builder.build(
            self._structural_report(structural_risk="HIGH"),
            cabinet_height=1800,
        )

        self.assertEqual(report.tipping_risk, "HIGH")

    def test_wide_cabinet_creates_medium_span_risk(self):
        report = self.builder.build(self._structural_report(), cabinet_width=1000)

        self.assertEqual(report.large_span_risk, "MEDIUM")

    def test_high_anti_racking_risk_creates_high_span_risk(self):
        report = self.builder.build(
            self._structural_report(anti_racking_risk="HIGH"),
            cabinet_width=900,
        )

        self.assertEqual(report.large_span_risk, "HIGH")

    def test_high_tipping_risk_requires_wall_anchoring(self):
        report = self.builder.build(
            self._structural_report(structural_risk="HIGH"),
            cabinet_height=1800,
        )

        self.assertTrue(report.wall_anchoring_required)

    def test_recommendation_propagation(self):
        report = self.builder.build(
            self._structural_report(structural_risk="HIGH"),
            cabinet_height=1800,
        )

        self.assertEqual(
            report.stability_recommendation,
            "Cabinet should be anchored and structurally reviewed",
        )

    def test_safe_defaults(self):
        report = self.builder.build(self._structural_report())

        self.assertEqual(report.tipping_risk, "LOW")
        self.assertFalse(report.wall_anchoring_required)
        self.assertEqual(report.large_span_risk, "LOW")
        self.assertEqual(report.stability_recommendation, "")

    def test_builder_does_not_mutate_inputs(self):
        structural = self._structural_report(
            structural_risk="HIGH",
            anti_racking_risk="MEDIUM",
            tags=["a", "b"],
        )
        snapshot = self._snapshot(structural)

        self.builder.build(structural, cabinet_height=1800, cabinet_width=1000)

        self.assertEqual(self._snapshot(structural), snapshot)

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _structural_report(
        structural_risk="LOW",
        anti_racking_risk="LOW",
        tags=None,
    ):
        report = SimpleNamespace(
            structural_risk=structural_risk,
            anti_racking_risk=anti_racking_risk,
        )
        report.tags = list(tags or [])
        return report


if __name__ == "__main__":
    unittest.main()
