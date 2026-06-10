import unittest

from exports.cutlist_engine import CutListItem
from exports.nesting_engine import IndustrialNestingEngine, NestingPart
from exports.strategies import GuillotineStripStrategy, PlacementStrategy


class CaptureStrategy(PlacementStrategy):

    def __init__(self):
        self.calls = []

    def pack(self, parts, sheet_w, sheet_h, kerf):
        self.calls.append(list(parts))
        return []


class TestNestingQualityAudit(unittest.TestCase):

    def test_current_behavior_groups_by_material_and_thickness(self):
        """Current behavior: thickness splits material nesting baskets."""
        strategy = CaptureStrategy()
        items = [
            CutListItem("P18", 30, 20, 18, "MDF", "Test", "SHELF"),
            CutListItem("P08", 30, 20, 8, "MDF", "Test", "BACK_PANEL"),
        ]

        result = IndustrialNestingEngine(strategy).process(items)

        self.assertEqual(list(result), ["MDF_18MM", "MDF_8MM"])
        self.assertEqual(len(strategy.calls), 2)
        self.assertEqual([len(parts) for parts in strategy.calls], [1, 1])

    def test_current_multi_sheet_overflow_starts_a_new_sheet(self):
        """Current behavior: a part that cannot enter the next strip starts a new sheet."""
        parts = [
            NestingPart("P1", 80, 40, False),
            NestingPart("P2", 80, 40, False),
        ]

        sheets = GuillotineStripStrategy().pack(parts, 100, 100, 4)

        self.assertEqual(len(sheets), 2)
        self.assertEqual([sheet.sheet_id for sheet in sheets], [1, 2])
        self.assertEqual([len(sheet.placed_parts) for sheet in sheets], [1, 1])

    def test_current_rotation_rotates_tall_grain_free_part(self):
        """Current behavior: a rotatable part taller than wide is rotated."""
        part = NestingPart("ROTATABLE", 40, 60, True)

        sheets = GuillotineStripStrategy().pack([part], 100, 100, 4)

        placed = sheets[0].placed_parts[0]
        self.assertTrue(placed.rotated)
        self.assertEqual((placed.placed_width, placed.placed_height), (60, 40))

    def test_current_grain_restriction_prevents_rotation(self):
        """Current behavior: a grain-restricted part preserves its orientation."""
        part = NestingPart("GRAIN_RESTRICTED", 40, 60, False)

        sheets = GuillotineStripStrategy().pack([part], 100, 100, 4)

        placed = sheets[0].placed_parts[0]
        self.assertFalse(placed.rotated)
        self.assertEqual((placed.placed_width, placed.placed_height), (40, 60))

    def test_current_oversized_part_is_silently_omitted(self):
        """Current behavior: an oversized part is omitted without a rejected-parts result."""
        oversized = NestingPart("OVERSIZED", 90, 20, False)

        sheets = GuillotineStripStrategy().pack([oversized], 100, 100, 4)

        self.assertEqual(sheets, [])

    def test_current_used_area_is_sum_of_placed_part_areas(self):
        """Current behavior: used area excludes trim and kerf and sums part rectangles."""
        parts = [
            NestingPart("P1", 30, 20, False),
            NestingPart("P2", 30, 20, False),
        ]

        sheets = GuillotineStripStrategy().pack(parts, 100, 100, 4)

        self.assertEqual(len(sheets), 1)
        self.assertEqual(sheets[0].used_area, 1200)

    def test_current_kerf_is_spacing_between_parts_in_same_strip(self):
        """Current behavior: horizontal spacing between adjacent parts equals the kerf."""
        parts = [
            NestingPart("P1", 30, 20, False),
            NestingPart("P2", 30, 20, False),
        ]

        sheets = GuillotineStripStrategy().pack(parts, 100, 100, 4)

        first, second = sheets[0].strips[0].parts
        spacing = second.x - (first.x + first.placed_width)
        self.assertEqual(spacing, 4)


if __name__ == "__main__":
    unittest.main()
