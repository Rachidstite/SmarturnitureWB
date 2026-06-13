import unittest
from dataclasses import fields, is_dataclass


class TestOffcutIntelligenceBuilder(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.offcut_intelligence_builder import (
            OffcutIntelligenceBuilder,
        )

        self.builder = OffcutIntelligenceBuilder()

    def test_report_is_dataclass_with_required_fields(self):
        from cost_intelligence.offcut_intelligence_report import (
            OffcutIntelligenceReport,
        )

        self.assertTrue(is_dataclass(OffcutIntelligenceReport))
        self.assertEqual(
            [field.name for field in fields(OffcutIntelligenceReport)],
            [
                "reuse_rate",
                "waste_recovery_score",
                "recommendation",
                "warnings",
            ],
        )

    def test_empty_report_has_no_reuse_recommendation(self):
        report = self._offcut_report()

        intelligence = self.builder.build(report)

        self.assertEqual(intelligence.reuse_rate, 0.0)
        self.assertEqual(intelligence.waste_recovery_score, 0)
        self.assertEqual(
            intelligence.recommendation,
            "No offcuts available for reuse",
        )

    def test_good_reuse_potential(self):
        report = self._offcut_report(total_offcuts=10, reusable_offcuts=7)

        intelligence = self.builder.build(report)

        self.assertEqual(intelligence.reuse_rate, 0.7)
        self.assertEqual(intelligence.waste_recovery_score, 70)
        self.assertEqual(
            intelligence.recommendation,
            "Good offcut reuse potential",
        )

    def test_moderate_reuse_potential(self):
        report = self._offcut_report(total_offcuts=10, reusable_offcuts=4)

        intelligence = self.builder.build(report)

        self.assertEqual(intelligence.reuse_rate, 0.4)
        self.assertEqual(intelligence.waste_recovery_score, 40)
        self.assertEqual(
            intelligence.recommendation,
            "Moderate offcut reuse potential",
        )

    def test_low_reuse_potential_and_integer_score(self):
        report = self._offcut_report(total_offcuts=3, reusable_offcuts=1)

        intelligence = self.builder.build(report)

        self.assertEqual(intelligence.reuse_rate, 1 / 3)
        self.assertEqual(intelligence.waste_recovery_score, 33)
        self.assertEqual(
            intelligence.recommendation,
            "Low offcut reuse potential",
        )

    def test_builder_preserves_warnings(self):
        warnings = ["Offcut warning"]
        report = self._offcut_report(warnings=warnings)

        intelligence = self.builder.build(report)

        self.assertIs(intelligence.warnings, warnings)

    @staticmethod
    def _offcut_report(**values):
        from cost_intelligence.offcut_report import OffcutReport

        return OffcutReport(**values)


if __name__ == "__main__":
    unittest.main()
