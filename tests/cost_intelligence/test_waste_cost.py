import unittest
from dataclasses import fields

from exports.nesting_engine import NestingPart
from exports.strategies import GuillotineStripStrategy, SheetResult


class TestWasteCostCharacterization(unittest.TestCase):

    def test_nesting_tracks_placed_part_area_but_not_waste_cost(self):
        sheets = GuillotineStripStrategy(trim_cut=10).pack(
            [
                NestingPart("P1", 100, 50, False),
                NestingPart("P2", 100, 50, False),
            ],
            sheet_w=300,
            sheet_h=200,
            kerf=4,
        )

        self.assertEqual(len(sheets), 1)
        self.assertEqual(sheets[0].used_area, 10_000)

        field_names = {field.name for field in fields(SheetResult)}
        self.assertNotIn("waste_area", field_names)
        self.assertNotIn("waste_percentage", field_names)
        self.assertNotIn("waste_cost", field_names)

    def test_oversized_rejected_part_produces_no_sheet_or_waste_record(self):
        sheets = GuillotineStripStrategy(trim_cut=10).pack(
            [NestingPart("TOO_LARGE", 500, 500, False)],
            sheet_w=300,
            sheet_h=200,
            kerf=4,
        )

        self.assertEqual(sheets, [])


if __name__ == "__main__":
    unittest.main()
