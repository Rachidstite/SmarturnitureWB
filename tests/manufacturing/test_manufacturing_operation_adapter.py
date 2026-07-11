import unittest


class TestManufacturingOperationAdapter(unittest.TestCase):

    def test_converts_machining_operation_to_unified_operation(self):
        from domain.core_types import MachiningOperation
        from manufacturing.manufacturing_operation_adapter import (
            ManufacturingOperationAdapter,
        )
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )

        operation = MachiningOperation(
            op_type="DRILL",
            diameter=5.0,
            depth=12.0,
            face="TOP",
            local_x=10.0,
            local_y=20.0,
            axis="X",
            is_through=True,
        )

        unified = ManufacturingOperationAdapter.to_unified(operation)

        self.assertIsInstance(unified, UnifiedManufacturingOperation)
        self.assertEqual(unified.operation_type, "DRILL")
        self.assertEqual(unified.metadata["original_operation_type"], "DRILL")

    def test_converts_face_drill_to_unified_operation(self):
        from domain.manufacturing_ops import FaceDrill
        from manufacturing.manufacturing_operation_adapter import (
            ManufacturingOperationAdapter,
        )
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )

        operation = FaceDrill(
            x=10.0,
            y=20.0,
            diameter=5.0,
            depth=12.0,
            face="TOP",
        )

        unified = ManufacturingOperationAdapter.to_unified(operation)

        self.assertIsInstance(unified, UnifiedManufacturingOperation)
        self.assertEqual(unified.operation_type, "DRILL")
        self.assertEqual(unified.source, "FaceDrill")

    def test_converts_edge_drill_to_unified_operation(self):
        from domain.manufacturing_ops import EdgeDrill
        from manufacturing.manufacturing_operation_adapter import (
            ManufacturingOperationAdapter,
        )
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )

        operation = EdgeDrill(
            x=10.0,
            z=7.0,
            diameter=5.0,
            depth=12.0,
            edge="LEFT",
        )

        unified = ManufacturingOperationAdapter.to_unified(operation)

        self.assertIsInstance(unified, UnifiedManufacturingOperation)
        self.assertEqual(unified.operation_type, "DRILL")
        self.assertEqual(unified.source, "EdgeDrill")

    def test_converts_groove_to_unified_operation(self):
        from domain.manufacturing_ops import Groove
        from manufacturing.manufacturing_operation_adapter import (
            ManufacturingOperationAdapter,
        )
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )

        operation = Groove(
            start_x=10.0,
            start_y=20.0,
            width=4.0,
            depth=6.0,
            length=100.0,
            face="BACK",
        )

        unified = ManufacturingOperationAdapter.to_unified(operation)

        self.assertIsInstance(unified, UnifiedManufacturingOperation)
        self.assertEqual(unified.operation_type, "GROOVE")
        self.assertEqual(unified.source, "Groove")

    def test_returns_unified_operation_unchanged(self):
        from manufacturing.manufacturing_operation_adapter import (
            ManufacturingOperationAdapter,
        )
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )

        operation = UnifiedManufacturingOperation(operation_type="DRILL")

        unified = ManufacturingOperationAdapter.to_unified(operation)

        self.assertIs(unified, operation)

    def test_preserves_supported_operation_fields(self):
        from domain.core_types import MachiningOperation
        from manufacturing.manufacturing_operation_adapter import (
            ManufacturingOperationAdapter,
        )

        operation = MachiningOperation(
            op_type="DRILL",
            diameter=8.0,
            depth=16.0,
            face="BOTTOM",
            local_x=11.0,
            local_y=22.0,
            axis="Y",
            is_through=True,
        )
        operation.z = 3.0

        unified = ManufacturingOperationAdapter.to_unified(operation)

        self.assertEqual(unified.diameter, 8.0)
        self.assertEqual(unified.depth, 16.0)
        self.assertEqual(unified.face, "BOTTOM")
        self.assertEqual(unified.axis, "Y")
        self.assertTrue(unified.is_through)
        self.assertEqual(unified.x, 11.0)
        self.assertEqual(unified.y, 22.0)
        self.assertEqual(unified.z, 3.0)

    def test_to_unified_list_accepts_iterables(self):
        from domain.manufacturing_ops import FaceDrill
        from manufacturing.manufacturing_operation_adapter import (
            ManufacturingOperationAdapter,
        )

        operations = (
            FaceDrill(
                x=float(index),
                y=2.0,
                diameter=5.0,
                depth=12.0,
                face="TOP",
            )
            for index in range(2)
        )

        unified_operations = ManufacturingOperationAdapter.to_unified_list(
            operations
        )

        self.assertEqual(len(unified_operations), 2)
        self.assertEqual(
            [operation.operation_type for operation in unified_operations],
            ["DRILL", "DRILL"],
        )

    def test_to_unified_injects_panel_identity_when_panel_context_is_provided(self):
        from domain.manufacturing_ops import FaceDrill
        from manufacturing.manufacturing_operation_adapter import (
            ManufacturingOperationAdapter,
        )

        operation = FaceDrill(
            x=10.0,
            y=20.0,
            diameter=5.0,
            depth=12.0,
            face="TOP",
        )

        unified = ManufacturingOperationAdapter.to_unified(
            operation,
            panel_identity="PANEL-01",
        )

        self.assertEqual(unified.metadata["panel_identity"], "PANEL-01")


if __name__ == "__main__":
    unittest.main()
