import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestCabinetEngineeringBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.cabinet_engineering_builder import (
            CabinetEngineeringBuilder,
        )

        self.builder = CabinetEngineeringBuilder()

    def test_report_contract(self):
        from manufacturing.cabinet_engineering_report import CabinetEngineeringReport

        self.assertTrue(is_dataclass(CabinetEngineeringReport))
        self.assertEqual(
            [field.name for field in fields(CabinetEngineeringReport)],
            [
                "cabinet_height_risk",
                "cabinet_width_risk",
                "center_divider_required",
                "wall_anchoring_recommended",
                "shelf_support_recommended",
                "engineering_recommendation",
            ],
        )

        report = CabinetEngineeringReport()

        self.assertEqual(report.cabinet_height_risk, "LOW")
        self.assertEqual(report.cabinet_width_risk, "LOW")
        self.assertFalse(report.center_divider_required)
        self.assertFalse(report.wall_anchoring_recommended)
        self.assertFalse(report.shelf_support_recommended)
        self.assertEqual(report.engineering_recommendation, "")

    def test_tall_height_creates_medium_risk(self):
        report = self.builder.build(cabinet_height=1800)

        self.assertEqual(report.cabinet_height_risk, "MEDIUM")

    def test_very_tall_height_creates_high_risk(self):
        report = self.builder.build(cabinet_height=2200)

        self.assertEqual(report.cabinet_height_risk, "HIGH")

    def test_wide_width_creates_medium_risk(self):
        report = self.builder.build(cabinet_width=1000)

        self.assertEqual(report.cabinet_width_risk, "MEDIUM")

    def test_very_wide_width_creates_high_risk(self):
        report = self.builder.build(cabinet_width=1200)

        self.assertEqual(report.cabinet_width_risk, "HIGH")

    def test_high_width_requires_center_divider(self):
        report = self.builder.build(cabinet_width=1200)

        self.assertTrue(report.center_divider_required)

    def test_high_height_recommends_wall_anchoring(self):
        report = self.builder.build(cabinet_height=2200)

        self.assertTrue(report.wall_anchoring_recommended)

    def test_high_width_or_height_recommends_shelf_support(self):
        wide_report = self.builder.build(cabinet_width=1200)
        tall_report = self.builder.build(cabinet_height=2200)

        self.assertTrue(wide_report.shelf_support_recommended)
        self.assertTrue(tall_report.shelf_support_recommended)

    def test_high_risk_requires_review(self):
        report = self.builder.build(cabinet_height=2200, cabinet_width=1200)

        self.assertEqual(report.engineering_recommendation, "Cabinet engineering review required")

    def test_medium_risk_recommends_review(self):
        report = self.builder.build(cabinet_height=1800, cabinet_width=1000)

        self.assertEqual(report.engineering_recommendation, "Cabinet engineering review recommended")

    def test_safe_defaults(self):
        report = self.builder.build()

        self.assertEqual(report.cabinet_height_risk, "LOW")
        self.assertEqual(report.cabinet_width_risk, "LOW")
        self.assertFalse(report.center_divider_required)
        self.assertFalse(report.wall_anchoring_recommended)
        self.assertFalse(report.shelf_support_recommended)
        self.assertEqual(report.engineering_recommendation, "")

    def test_builder_does_not_mutate_inputs(self):
        height = SimpleNamespace(value=1800)
        width = SimpleNamespace(value=1000)
        snapshot = self._snapshot((height, width))

        self.builder.build(cabinet_height=height.value, cabinet_width=width.value)

        self.assertEqual(self._snapshot((height, width)), snapshot)

    @staticmethod
    def _snapshot(items):
        return [
            {
                key: list(value) if isinstance(value, list) else value
                for key, value in item.__dict__.items()
            }
            for item in items
        ]


if __name__ == "__main__":
    unittest.main()
