import unittest

from domain.core_types import MachiningOperation as CoreMachiningOperation
from domain.hardware_domain import MachiningOperation as HardwareMachiningOperation
from domain.topology import Transform3D

from manufacturing.machining_operation_adapter import \
    MachiningOperationAdapter


class TestMachiningOperationAdapter(unittest.TestCase):

    def test_core_type_operation_to_unified(self):

        op = CoreMachiningOperation(
            op_type="DRILL",
            diameter=15,
            depth=12,
            face="TOP",
            local_x=34,
            local_y=64
        )

        unified = (
            MachiningOperationAdapter
            .from_operation(op)
        )

        self.assertEqual(
            unified.operation_type,
            "DRILL"
        )

        self.assertEqual(
            unified.source,
            "modern-core"
        )

        self.assertEqual(
            unified.x,
            34
        )

        self.assertEqual(
            unified.y,
            64
        )

    def test_hardware_operation_to_unified(self):

        op = HardwareMachiningOperation(
            op_type="DRILL",
            diameter=8,
            depth=10,
            transform=Transform3D(
                x=100,
                y=200,
                z=5
            )
        )

        unified = (
            MachiningOperationAdapter
            .from_operation(op)
        )

        self.assertEqual(
            unified.operation_type,
            "DRILL"
        )

        self.assertEqual(
            unified.source,
            "modern-hardware"
        )

        self.assertEqual(
            unified.x,
            100
        )

        self.assertEqual(
            unified.y,
            200
        )

        self.assertEqual(
            unified.z,
            5
        )


if __name__ == "__main__":
    unittest.main()
