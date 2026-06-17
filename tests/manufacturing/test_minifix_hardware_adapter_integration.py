import unittest


class TestMinifixHardwareAdapterIntegration(unittest.TestCase):

    def test_minifix_target_holes_convert_to_manufacturing_operations(self):
        from domain.manufacturing_ops import EdgeDrill, FaceDrill
        from domain.hardware_library import HardwareRegistry
        from manufacturing.hardware_operation_adapter import (
            HardwareOperationAdapter,
        )

        hardware = HardwareRegistry().get_hardware("MINIFIX_15_V1")
        operations = HardwareOperationAdapter.to_unified(hardware.target_holes)

        self.assertEqual(len(operations), 2)
        self.assertIsInstance(operations[0], FaceDrill)
        self.assertIsInstance(operations[1], EdgeDrill)

        self.assertEqual(operations[0].diameter, 15)
        self.assertEqual(operations[0].depth, 14)
        self.assertEqual(operations[1].diameter, 8)
        self.assertEqual(operations[1].depth, 34)

        self.assertEqual(operations[0].face, "FRONT")
        self.assertEqual(operations[1].edge, "LEFT")


if __name__ == "__main__":
    unittest.main()
