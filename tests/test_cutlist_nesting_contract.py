import unittest
from types import SimpleNamespace
from unittest.mock import patch

from exports.cutlist_engine import CutListEngine, CutListItem
from exports.nesting_engine import IndustrialNestingEngine
from exports.strategies import PlacementStrategy
from manufacturing.panel_spec import PanelSpec
from shared.roles import NodeRole


class CaptureStrategy(PlacementStrategy):

    def __init__(self):
        self.parts = []

    def pack(self, parts, sheet_w, sheet_h, kerf):
        self.parts.extend(parts)
        return []


class TestCutListNestingContract(unittest.TestCase):

    def test_cutlist_item_can_enter_nesting_engine(self):
        strategy = CaptureStrategy()
        engine = IndustrialNestingEngine(strategy)
        item = CutListItem(
            identity="SHELF_1",
            width=600,
            height=400,
            thickness=18,
            material="MDF",
            group="Shelves",
            role="SHELF",
        )

        engine.process([item])

        self.assertEqual(len(strategy.parts), 1)
        self.assertEqual(strategy.parts[0].width, 600)
        self.assertEqual(strategy.parts[0].height, 400)

    def test_quantity_expands_nesting_parts(self):
        strategy = CaptureStrategy()
        engine = IndustrialNestingEngine(strategy)
        item = CutListItem(
            identity="SHELF_1",
            width=600,
            height=400,
            thickness=18,
            material="MDF",
            group="Shelves",
            role="SHELF",
            quantity=3,
        )

        engine.process([item])

        self.assertEqual(len(strategy.parts), 3)

    def test_legacy_cut_dimensions_are_supported(self):
        strategy = CaptureStrategy()
        engine = IndustrialNestingEngine(strategy)
        legacy_item = SimpleNamespace(
            identity="LEGACY_SHELF_1",
            cut_width=580,
            cut_height=380,
            thickness=18,
            material="MDF",
            group="Shelves",
            role="SHELF",
            grain_direction="NONE",
            quantity=1,
        )

        engine.process([legacy_item])

        self.assertEqual(len(strategy.parts), 1)
        self.assertEqual(strategy.parts[0].width, 580)
        self.assertEqual(strategy.parts[0].height, 380)

    def test_grain_direction_is_propagated_from_panel_spec(self):
        spec = PanelSpec(
            identity="SHELF_1",
            role=NodeRole.SHELF,
            width=600,
            height=400,
            thickness=18,
            material="MDF",
            grain_direction="VERTICAL",
        )

        with patch(
            "exports.cutlist_engine.ManufacturingExtractor.extract",
            return_value=[spec],
        ):
            items = CutListEngine.extract(SimpleNamespace())

        self.assertEqual(items[0].grain_direction, "VERTICAL")


if __name__ == "__main__":
    unittest.main()
