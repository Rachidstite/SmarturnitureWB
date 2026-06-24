import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestShelfStructuralBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.shelf_structural_builder import ShelfStructuralBuilder

        self.builder = ShelfStructuralBuilder()

    def test_report_contract(self):
        from manufacturing.shelf_structural_report import ShelfStructuralReport

        self.assertTrue(is_dataclass(ShelfStructuralReport))
        self.assertEqual(
            [field.name for field in fields(ShelfStructuralReport)],
            [
                "span_risk",
                "sagging_risk",
                "support_required",
                "shelf_recommendation",
            ],
        )

        report = ShelfStructuralReport()

        self.assertEqual(report.span_risk, "LOW")
        self.assertEqual(report.sagging_risk, "LOW")
        self.assertFalse(report.support_required)
        self.assertEqual(report.shelf_recommendation, "")

    def test_width_medium_creates_medium_span_risk(self):
        report = self.builder.build(shelf_width=800)

        self.assertEqual(report.span_risk, "MEDIUM")

    def test_width_high_creates_high_span_risk(self):
        report = self.builder.build(shelf_width=1000)

        self.assertEqual(report.span_risk, "HIGH")

    def test_high_width_and_thin_shelf_creates_high_sagging_risk(self):
        report = self.builder.build(shelf_width=1000, shelf_thickness=18)

        self.assertEqual(report.sagging_risk, "HIGH")

    def test_high_span_requires_support(self):
        report = self.builder.build(shelf_width=1000)

        self.assertTrue(report.support_required)

    def test_recommendation_for_high_risk(self):
        report = self.builder.build(shelf_width=1000)

        self.assertEqual(report.shelf_recommendation, "Shelf support recommended")

    def test_recommendation_for_medium_risk(self):
        report = self.builder.build(shelf_width=800)

        self.assertEqual(report.shelf_recommendation, "Shelf span should be reviewed")

    def test_safe_defaults(self):
        report = self.builder.build()

        self.assertEqual(report.span_risk, "LOW")
        self.assertEqual(report.sagging_risk, "LOW")
        self.assertFalse(report.support_required)
        self.assertEqual(report.shelf_recommendation, "")

    def test_builder_does_not_mutate_inputs(self):
        shelf = SimpleNamespace(width=1000, thickness=18, tags=["a", "b"])
        snapshot = self._snapshot(shelf)

        self.builder.build(shelf_width=shelf.width, shelf_thickness=shelf.thickness)

        self.assertEqual(self._snapshot(shelf), snapshot)

    @staticmethod
    def _snapshot(item):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in item.__dict__.items()
        }


if __name__ == "__main__":
    unittest.main()
