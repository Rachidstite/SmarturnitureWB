import unittest

from cost_intelligence.remaining_region import RemainingRegion
from exports.nesting_engine import NestingPart
from exports.strategies import GuillotineStripStrategy


class TestRemainingRegions(unittest.TestCase):

    def test_one_placed_part_generates_remaining_regions(self):

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

        self.assertTrue(
            sheet.remaining_regions,
        )

        for region in sheet.remaining_regions:
            self.assertIsInstance(
                region,
                RemainingRegion,
            )
            self.assertTrue(region.id)
            self.assertGreaterEqual(region.x, 0)
            self.assertGreaterEqual(region.y, 0)
            self.assertGreater(region.width, 0)
            self.assertGreater(region.height, 0)
            self.assertGreater(region.area, 0)
            self.assertEqual(
                region.source_sheet,
                "SHEET-1",
            )


if __name__ == "__main__":
    unittest.main()
