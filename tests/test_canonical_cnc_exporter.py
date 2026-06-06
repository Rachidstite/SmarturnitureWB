import unittest

from manufacturing.panel_spec import PanelSpec

from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation
)

from exports.canonical_cnc_exporter import (
    CanonicalCNCExporter
)

from shared.roles import NodeRole


class TestCanonicalCNCExporter(unittest.TestCase):

    def test_export_rows(self):

        spec = PanelSpec(
            identity="PANEL_A",
            role=NodeRole.SHELF,
            width=600,
            height=300,
            thickness=18,
            material="MDF"
        )

        spec.unified_operations = [
            UnifiedManufacturingOperation(
                operation_type="DRILL",
                diameter=8,
                depth=30,
                is_through=True,
                x=10,
                y=20,
                z=5,
                face="TOP",
                axis="X",
                source="modern-core"
            )
        ]

        rows = (
            CanonicalCNCExporter
            .export_rows([spec])
        )

        self.assertEqual(
            len(rows),
            1
        )

        self.assertEqual(
            rows[0].panel_id,
            "PANEL_A"
        )

        self.assertEqual(
            rows[0].axis,
            "X"
        )

        self.assertTrue(
            rows[0].is_through
        )


if __name__ == "__main__":
    unittest.main()
