import unittest
from types import SimpleNamespace

from manufacturing.joint_operation_generator import (
    JointOperationGenerator
)
from domain.manufacturing_ops import (
    FaceDrill,
    EdgeDrill
)


class TestJointOperationGenerator(unittest.TestCase):

    def test_minifix_joint_generates_expected_operations(self):

        parent = SimpleNamespace(
            thickness=18.0,
            width=600,
            depth=500,
            height=720
        )

        child = SimpleNamespace(
            thickness=18.0,
            width=564,
            depth=500,
            height=18
        )

        ops = JointOperationGenerator.minifix_joint(
            parent,
            child
        )

        self.assertEqual(
            len(ops),
            2
        )

        self.assertIsInstance(
            ops[0],
            FaceDrill
        )

        self.assertEqual(
            ops[0].x,
            34
        )

        self.assertEqual(
            ops[0].y,
            64
        )

        self.assertEqual(
            ops[0].diameter,
            15
        )

        self.assertEqual(
            ops[0].depth,
            12
        )

        self.assertEqual(
            ops[0].face,
            "TOP"
        )

        self.assertIsInstance(
            ops[1],
            EdgeDrill
        )

        self.assertEqual(
            ops[1].x,
            64
        )

        self.assertEqual(
            ops[1].z,
            9.0
        )

        self.assertEqual(
            ops[1].diameter,
            8
        )

        self.assertEqual(
            ops[1].depth,
            30
        )

        self.assertEqual(
            ops[1].edge,
            "TOP"
        )


if __name__ == "__main__":
    unittest.main()
