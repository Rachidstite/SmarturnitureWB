import unittest
from types import SimpleNamespace


class TestMinifixLegacyVsHardwareEquivalence(unittest.TestCase):

    def test_legacy_and_hardware_minifix_depths_are_characterized_as_different(self):
        from domain.hardware_library import HardwareRegistry
        from manufacturing.joint_operation_generator import (
            JointOperationGenerator,
        )

        parent = SimpleNamespace(thickness=18.0)
        child = SimpleNamespace(thickness=18.0)

        legacy_ops = JointOperationGenerator.minifix_joint(parent, child)
        hardware = HardwareRegistry().get_hardware("MINIFIX_15_V1")
        hardware_ops = JointOperationGenerator.minifix_joint_from_hardware(
            parent,
            child,
            hardware,
        )

        self.assertEqual(len(legacy_ops), len(hardware_ops))
        self.assertEqual(
            [type(operation) for operation in legacy_ops],
            [type(operation) for operation in hardware_ops],
        )
        self.assertEqual(
            [operation.diameter for operation in legacy_ops],
            [operation.diameter for operation in hardware_ops],
        )
        self.assertEqual(
            [getattr(operation, "face", getattr(operation, "edge", "")) for operation in legacy_ops],
            ["TOP", "TOP"],
        )
        self.assertEqual(
            [getattr(operation, "face", getattr(operation, "edge", "")) for operation in hardware_ops],
            ["FRONT", "LEFT"],
        )
        self.assertEqual([operation.depth for operation in legacy_ops], [12, 30])
        self.assertEqual([operation.depth for operation in hardware_ops], [14, 34])


if __name__ == "__main__":
    unittest.main()
