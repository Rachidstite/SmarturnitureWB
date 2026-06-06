import unittest

from manufacturing.canonical_cnc_mapper import CanonicalCNCMapper
from manufacturing.canonical_cnc_row import CanonicalCNCRow
from manufacturing.panel_spec import PanelSpec
from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)
from shared.roles import NodeRole


class TestCanonicalCNCMapper(unittest.TestCase):

    def test_from_unified_operation_preserves_all_fields(self):
        panel_spec = PanelSpec(
            identity="PANEL_A",
            role=NodeRole.SHELF,
            width=600,
            height=300,
            thickness=18,
            material="MDF_18",
        )

        operation = UnifiedManufacturingOperation(
            operation_type="DRILL",
            diameter=8,
            depth=30,
            is_through=True,
            x=12.5,
            y=24.0,
            z=3.0,
            face="TOP",
            axis="X",
            source="modern-core",
        )

        row = CanonicalCNCMapper.from_unified_operation(panel_spec, operation)

        expected = CanonicalCNCRow(
            panel_id="PANEL_A",
            panel_role=str(NodeRole.SHELF),
            operation_type="DRILL",
            face="TOP",
            axis="X",
            x=12.5,
            y=24.0,
            z=3.0,
            diameter=8,
            depth=30,
            is_through=True,
            source="modern-core",
        )

        self.assertEqual(row, expected)
        self.assertEqual(row.axis, "X")
        self.assertEqual(row.source, "modern-core")
        self.assertTrue(row.is_through)
        self.assertEqual(row.panel_id, "PANEL_A")


if __name__ == "__main__":
    unittest.main()
