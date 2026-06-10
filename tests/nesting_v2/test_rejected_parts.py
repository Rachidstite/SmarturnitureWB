import unittest

from exports.nesting_engine import NestingPart
from exports.strategies import GuillotineStripStrategy


class TestRejectedParts(unittest.TestCase):

    def test_current_oversized_part_is_silently_dropped(self):

        parts = [
            NestingPart("OVERSIZED", 500, 500, False),
        ]

        sheets = GuillotineStripStrategy().pack(
            parts,
            sheet_w=300,
            sheet_h=200,
            kerf=4,
        )

        self.assertEqual(
            sheets,
            [],
        )


if __name__ == "__main__":
    unittest.main()
