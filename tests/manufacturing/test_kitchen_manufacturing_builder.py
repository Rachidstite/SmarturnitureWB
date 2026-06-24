import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestKitchenManufacturingBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.kitchen_manufacturing_builder import (
            KitchenManufacturingBuilder,
        )

        self.builder = KitchenManufacturingBuilder()

    def test_report_contract(self):
        from manufacturing.kitchen_manufacturing_report import (
            KitchenManufacturingReport,
        )

        self.assertTrue(is_dataclass(KitchenManufacturingReport))
        self.assertEqual(
            [field.name for field in fields(KitchenManufacturingReport)],
            [
                "cabinet_count",
                "drawer_count",
                "door_count",
                "manufacturing_complexity",
                "requires_engineering_review",
                "manufacturing_recommendation",
            ],
        )

        report = KitchenManufacturingReport()

        self.assertEqual(report.cabinet_count, 0)
        self.assertEqual(report.drawer_count, 0)
        self.assertEqual(report.door_count, 0)
        self.assertEqual(report.manufacturing_complexity, "LOW")
        self.assertFalse(report.requires_engineering_review)
        self.assertEqual(report.manufacturing_recommendation, "")

    def test_low_complexity_for_small_kitchen(self):
        report = self.builder.build(cabinet_count=5, drawer_count=5, door_count=5)

        self.assertEqual(report.manufacturing_complexity, "LOW")
        self.assertFalse(report.requires_engineering_review)
        self.assertEqual(report.manufacturing_recommendation, "")

    def test_medium_complexity_for_medium_kitchen(self):
        report = self.builder.build(cabinet_count=10, drawer_count=5, door_count=5)

        self.assertEqual(report.manufacturing_complexity, "MEDIUM")
        self.assertFalse(report.requires_engineering_review)
        self.assertEqual(
            report.manufacturing_recommendation,
            "Kitchen manufacturing review recommended",
        )

    def test_high_complexity_for_large_kitchen(self):
        report = self.builder.build(cabinet_count=20, drawer_count=15, door_count=15)

        self.assertEqual(report.manufacturing_complexity, "HIGH")
        self.assertTrue(report.requires_engineering_review)
        self.assertEqual(
            report.manufacturing_recommendation,
            "Kitchen manufacturing review required",
        )

    def test_engineering_review_flag_for_high_complexity(self):
        report = self.builder.build(cabinet_count=25, drawer_count=15, door_count=10)

        self.assertTrue(report.requires_engineering_review)

    def test_builder_does_not_mutate_inputs(self):
        counts = SimpleNamespace(cabinet_count=10, drawer_count=5, door_count=5)
        snapshot = self._snapshot(counts)

        self.builder.build(
            cabinet_count=counts.cabinet_count,
            drawer_count=counts.drawer_count,
            door_count=counts.door_count,
        )

        self.assertEqual(self._snapshot(counts), snapshot)

    @staticmethod
    def _snapshot(item):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in item.__dict__.items()
        }


if __name__ == "__main__":
    unittest.main()
