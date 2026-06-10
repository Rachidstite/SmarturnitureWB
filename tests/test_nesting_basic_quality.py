import unittest

from exports.nesting_engine import IndustrialNestingEngine
from exports.strategies import GuillotineStripStrategy
from exports.cutlist_engine import CutListItem


class TestNestingBasicQuality(unittest.TestCase):

    def test_simple_parts_fit_on_one_sheet(self):

        items = [
            CutListItem("P1", 600, 400, 18, "MDF", "Test", "SHELF"),
            CutListItem("P2", 600, 400, 18, "MDF", "Test", "SHELF"),
            CutListItem("P3", 1200, 300, 18, "MDF", "Test", "TOP"),
        ]

        result = IndustrialNestingEngine(
            GuillotineStripStrategy()
        ).process(items)

        sheets = result["MDF_18MM"]

        self.assertEqual(len(sheets), 1)
        self.assertEqual(len(sheets[0].placed_parts), 3)
        self.assertEqual(sheets[0].used_area, 840000)


if __name__ == "__main__":
    unittest.main()
