import unittest

from exports.cutlist_engine import CutListItem
from exports.nesting_engine import IndustrialNestingEngine
from exports.strategies import GuillotineStripStrategy


class TestNestingGroupsByMaterialAndThickness(unittest.TestCase):

    def test_parts_are_grouped_by_material_and_thickness(self):
        items = [
            CutListItem("P1", 600, 400, 18, "MDF", "Test", "SHELF"),
            CutListItem("P2", 600, 400, 8, "MDF", "Test", "BACK_PANEL"),
        ]

        result = IndustrialNestingEngine(
            GuillotineStripStrategy()
        ).process(items)

        self.assertEqual(
            set(result.keys()),
            {
                "MDF_18MM",
                "MDF_8MM",
            },
        )


if __name__ == "__main__":
    unittest.main()
