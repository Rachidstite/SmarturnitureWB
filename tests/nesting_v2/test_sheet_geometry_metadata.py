import unittest

from exports.nesting_engine import NestingPart
from exports.strategies import GuillotineStripStrategy, SheetResult


class TestSheetGeometryMetadata(unittest.TestCase):

    def test_existing_sheet_result_construction_has_safe_geometry_defaults(self):

        sheet = SheetResult(
            sheet_id=1,
        )

        self.assertEqual(
            sheet.sheet_width,
            0.0,
        )
        self.assertEqual(
            sheet.sheet_height,
            0.0,
        )
        self.assertEqual(
            sheet.kerf,
            0.0,
        )
        self.assertEqual(
            sheet.trim,
            0.0,
        )
        self.assertEqual(
            sheet.remaining_regions,
            [],
        )

    def test_remaining_regions_default_is_not_shared(self):

        first_sheet = SheetResult(
            sheet_id=1,
        )
        second_sheet = SheetResult(
            sheet_id=2,
        )

        first_sheet.remaining_regions.append(
            object(),
        )

        self.assertEqual(
            second_sheet.remaining_regions,
            [],
        )

    def test_guillotine_strategy_preserves_sheet_geometry_metadata(self):

        sheets = GuillotineStripStrategy(
            trim_cut=10,
        ).pack(
            [
                NestingPart(
                    "P1",
                    100,
                    50,
                    False,
                ),
            ],
            sheet_w=300,
            sheet_h=200,
            kerf=4,
        )

        sheet = sheets[0]

        self.assertEqual(
            sheet.sheet_width,
            300,
        )
        self.assertEqual(
            sheet.sheet_height,
            200,
        )
        self.assertEqual(
            sheet.kerf,
            4,
        )
        self.assertEqual(
            sheet.trim,
            10,
        )
        self.assertTrue(
            sheet.remaining_regions,
        )


if __name__ == "__main__":
    unittest.main()
