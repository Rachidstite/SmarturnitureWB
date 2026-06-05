import unittest

from domain.core_types import MachiningOperation

from manufacturing.machining_operation_adapter import \
    MachiningOperationAdapter


class TestMachiningOperationAdapter(unittest.TestCase):

    def test_core_type_operation_to_unified(self):

        op = MachiningOperation(
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


if __name__ == "__main__":
    unittest.main()
