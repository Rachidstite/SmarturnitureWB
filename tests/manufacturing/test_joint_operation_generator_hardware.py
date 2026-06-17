import unittest
from types import SimpleNamespace


class TestJointOperationGeneratorHardware(unittest.TestCase):

    def test_minifix_joint_from_hardware_uses_target_holes(self):
        from domain.hardware_library import HardwareRegistry
        from domain.manufacturing_ops import EdgeDrill, FaceDrill
        from manufacturing.joint_operation_generator import (
            JointOperationGenerator,
        )

        parent = SimpleNamespace(thickness=18.0)
        child = SimpleNamespace(thickness=18.0)
        hardware = HardwareRegistry().get_hardware("MINIFIX_15_V1")
        original_snapshot = [hole.__dict__.copy() for hole in hardware.target_holes]

        operations = JointOperationGenerator.minifix_joint_from_hardware(
            parent,
            child,
            hardware,
        )

        self.assertEqual(len(operations), 2)
        self.assertIsInstance(operations[0], FaceDrill)
        self.assertIsInstance(operations[1], EdgeDrill)

        self.assertEqual(operations[0].diameter, 15)
        self.assertEqual(operations[0].depth, 14)
        self.assertEqual(operations[1].diameter, 8)
        self.assertEqual(operations[1].depth, 34)
        self.assertEqual(operations[0].face, "FRONT")
        self.assertEqual(operations[1].edge, "LEFT")

        self.assertEqual(
            [hole.__dict__ for hole in hardware.target_holes],
            original_snapshot,
        )


if __name__ == "__main__":
    unittest.main()
