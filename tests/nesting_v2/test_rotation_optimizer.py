import unittest

from exports.nesting_engine import NestingPart
from exports.strategies import GuillotineStripStrategy


class TestRotationOptimizer(unittest.TestCase):

    def test_current_rotation_rule_rotates_tall_grain_free_part(self):

        parts = [
            NestingPart("TALL", 40, 80, True),
        ]

        sheets = GuillotineStripStrategy().pack(
            parts,
            sheet_w=300,
            sheet_h=200,
            kerf=4,
        )

        placed = sheets[0].placed_parts[0]

        self.assertTrue(
            placed.rotated,
        )

        self.assertEqual(
            placed.placed_width,
            80,
        )

        self.assertEqual(
            placed.placed_height,
            40,
        )


if __name__ == "__main__":
    unittest.main()
