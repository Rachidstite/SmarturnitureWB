import unittest

from exports.nesting_engine import NestingPart
from exports.strategies import GuillotineStripStrategy


class TestNestingUtilization(unittest.TestCase):

    def test_current_used_area_excludes_sheet_area_trim_and_kerf(self):

        parts = [
            NestingPart("P1", 100, 50, False),
            NestingPart("P2", 100, 50, False),
        ]

        sheets = GuillotineStripStrategy().pack(
            parts,
            sheet_w=300,
            sheet_h=200,
            kerf=4,
        )

        self.assertEqual(
            len(sheets),
            1,
        )

        self.assertEqual(
            sheets[0].used_area,
            10000,
        )


if __name__ == "__main__":
    unittest.main()
