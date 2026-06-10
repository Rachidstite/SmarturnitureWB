import unittest

from exports.nesting_engine import IndustrialNestingEngine
from exports.strategies import GuillotineStripStrategy
from exports.cutlist_engine import CutListItem


class TestNestingGroupsByMaterial(unittest.TestCase):

    def test_parts_are_grouped_by_material(self):

        items = [
            CutListItem("P1", 600, 400, 18, "MDF", "Test", "SHELF"),
            CutListItem("P2", 600, 400, 18, "PLYWOOD", "Test", "SHELF"),
        ]

        result = IndustrialNestingEngine(
            GuillotineStripStrategy()
        ).process(items)

        self.assertIn("MDF_18MM", result)
        self.assertIn("PLYWOOD_18MM", result)
        self.assertEqual(len(result["MDF_18MM"]), 1)
        self.assertEqual(len(result["PLYWOOD_18MM"]), 1)


if __name__ == "__main__":
    unittest.main()
