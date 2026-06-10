import unittest

from exports.nesting_engine import IndustrialNestingEngine
from exports.strategies import GuillotineStripStrategy
from exports.cutlist_engine import CutListItem


class TestNestingThicknessGroupingAudit(unittest.TestCase):

    def test_current_engine_groups_by_material_and_thickness(self):

        items = [
            CutListItem("P1", 600, 400, 18, "MDF", "Test", "SHELF"),
            CutListItem("P2", 600, 400, 8, "MDF", "Test", "BACK_PANEL"),
        ]

        result = IndustrialNestingEngine(
            GuillotineStripStrategy()
        ).process(items)

        self.assertEqual(
            list(result.keys()),
            ["MDF_18MM", "MDF_8MM"],
        )


if __name__ == "__main__":
    unittest.main()
