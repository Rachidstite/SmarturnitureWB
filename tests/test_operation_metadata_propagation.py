import unittest

from domain.core_types import MachiningOperation

from manufacturing.machining_operation_adapter import (
    MachiningOperationAdapter,
)


class TestOperationMetadataPropagation(
    unittest.TestCase
):

    def test_metadata_is_preserved(self):

        op = MachiningOperation(
            op_type="DRILL",
            diameter=5,
            depth=12,
            face="TOP",
            local_x=10,
            local_y=20,
            metadata={
                "hardware_intent": "INTENT_MINIFIX_15",
                "target_node_id": "SHELF_1",
            }
        )

        unified = (
            MachiningOperationAdapter
            .from_operation(op)
        )

        self.assertEqual(
            unified.metadata["hardware_intent"],
            "INTENT_MINIFIX_15"
        )

        self.assertEqual(
            unified.metadata["target_node_id"],
            "SHELF_1"
        )


if __name__ == "__main__":
    unittest.main()
