import unittest

from domain.core_types import MachiningOperation
from manufacturing.machining_operation_adapter import MachiningOperationAdapter


class TestMachiningOperationAdapter(unittest.TestCase):

    def test_modern_operation_preserves_is_through(self):
        op = MachiningOperation(
            op_type="DRILL",
            diameter=8,
            depth=30,
            face="TOP",
            local_x=12,
            local_y=24,
            is_through=True,
        )

        unified = MachiningOperationAdapter.from_operation(op)

        self.assertTrue(unified.is_through)


if __name__ == "__main__":
    unittest.main()
