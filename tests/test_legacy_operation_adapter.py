import unittest

from domain.manufacturing_ops import (
    FaceDrill,
    EdgeDrill
)

from manufacturing.legacy_operation_adapter import \
    LegacyOperationAdapter


class TestLegacyOperationAdapter(unittest.TestCase):

    def test_face_drill_to_unified(self):

        op = FaceDrill(
            x=34,
            y=64,
            diameter=15,
            depth=12,
            face="TOP"
        )

        unified = (
            LegacyOperationAdapter
            .from_operation(op)
        )

        self.assertEqual(
            unified.operation_type,
            "FACE_DRILL"
        )

        self.assertEqual(
            unified.source,
            "legacy"
        )

        self.assertEqual(
            unified.x,
            34
        )

        self.assertEqual(
            unified.y,
            64
        )

    def test_edge_drill_to_unified(self):

        op = EdgeDrill(
            x=64,
            z=9,
            diameter=8,
            depth=30,
            edge="TOP"
        )

        unified = (
            LegacyOperationAdapter
            .from_operation(op)
        )

        self.assertEqual(
            unified.operation_type,
            "EDGE_DRILL"
        )

        self.assertEqual(
            unified.source,
            "legacy"
        )

        self.assertEqual(
            unified.x,
            64
        )

        self.assertEqual(
            unified.z,
            9
        )


if __name__ == "__main__":
    unittest.main()
