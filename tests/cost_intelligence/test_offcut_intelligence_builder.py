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
                "reusable_area",
                "largest_reusable_area",
                "estimated_recovered_value",
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

    def test_builder_calculates_reusable_area_from_reusable_offcuts_only(self):
        reusable_small = self._offcut(width=100.0, height=200.0, reusable=True)
        reusable_large = self._offcut(width=300.0, height=400.0, reusable=True)
        non_reusable = self._offcut(width=1000.0, height=1000.0, reusable=False)
        report = self._offcut_report(
            offcuts=[reusable_small, reusable_large, non_reusable],
            total_offcuts=3,
            reusable_offcuts=2,
        )

        intelligence = self.builder.build(report)

        self.assertEqual(intelligence.reusable_area, 140000.0)
        self.assertEqual(intelligence.largest_reusable_area, 120000.0)

    def test_builder_estimates_recovered_value_from_square_meters(self):
        reusable = self._offcut(width=1000.0, height=500.0, reusable=True)
        report = self._offcut_report(
            offcuts=[reusable],
            total_offcuts=1,
            reusable_offcuts=1,
        )

        intelligence = self.builder.build(report, price_per_m2=200.0)

        self.assertEqual(intelligence.reusable_area, 500000.0)
        self.assertEqual(intelligence.estimated_recovered_value, 100.0)

    def test_builder_does_not_mutate_offcut_report_or_offcuts(self):
        reusable = self._offcut(width=100.0, height=200.0, reusable=True)
        non_reusable = self._offcut(width=300.0, height=400.0, reusable=False)
        report = self._offcut_report(
            offcuts=[reusable, non_reusable],
            total_offcuts=2,
            reusable_offcuts=1,
            warnings=["Offcut warning"],
        )
        original_report_values = report.__dict__.copy()
        original_offcut_values = [
            offcut.__dict__.copy()
            for offcut in report.offcuts
        ]

        self.builder.build(report, price_per_m2=200.0)

        self.assertEqual(report.__dict__, original_report_values)
        self.assertEqual(
            [offcut.__dict__ for offcut in report.offcuts],
            original_offcut_values,
        )

    @staticmethod
    def _offcut(**values):
        from cost_intelligence.offcut import Offcut

        defaults = {
            "id": "OFFCUT-001",
            "material": "MDF",
            "thickness": 18.0,
            "width": 100.0,
            "height": 100.0,
            "source_sheet": "SHEET-001",
        }
        defaults.update(values)
        return Offcut(**defaults)

    @staticmethod
    def _offcut_report(**values):
        from cost_intelligence.offcut_report import OffcutReport

        return OffcutReport(**values)


if __name__ == "__main__":
    unittest.main()
