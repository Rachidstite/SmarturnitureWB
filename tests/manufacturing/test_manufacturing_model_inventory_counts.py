import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingModelInventoryCounts(unittest.TestCase):

    def test_contract_is_dataclass(self):
        from manufacturing.manufacturing_model_inventory_counts import (
            ManufacturingModelInventoryCounts,
        )

        self.assertTrue(is_dataclass(ManufacturingModelInventoryCounts))

    def test_field_order_is_exact(self):
        from manufacturing.manufacturing_model_inventory_counts import (
            ManufacturingModelInventoryCounts,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingModelInventoryCounts)],
            [
                "cabinet_count",
                "door_count",
                "shelf_count",
                "back_panel_count",
            ],
        )

    def test_safe_defaults_are_zero(self):
        from manufacturing.manufacturing_model_inventory_counts import (
            ManufacturingModelInventoryCounts,
        )

        counts = ManufacturingModelInventoryCounts()

        self.assertEqual(counts.cabinet_count, 0)
        self.assertEqual(counts.door_count, 0)
        self.assertEqual(counts.shelf_count, 0)
        self.assertEqual(counts.back_panel_count, 0)


if __name__ == "__main__":
    unittest.main()
