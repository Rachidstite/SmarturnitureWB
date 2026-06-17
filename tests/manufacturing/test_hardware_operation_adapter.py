import unittest


class TestHardwareOperationAdapter(unittest.TestCase):

    def test_converts_15mm_minifix_cam_hole_to_facedrill(self):
        from domain.anchors import MountFace
        from domain.hardware_library import HoleSpec
        from domain.manufacturing_ops import FaceDrill
        from manufacturing.hardware_operation_adapter import (
            HardwareOperationAdapter,
        )

        hole = HoleSpec(
            diameter=15.0,
            depth=14.0,
            face=MountFace.FRONT,
            offset_x=34.0,
            offset_y=0.0,
        )

        operations = HardwareOperationAdapter.to_unified([hole])

        self.assertEqual(len(operations), 1)
        self.assertIsInstance(operations[0], FaceDrill)
        self.assertEqual(operations[0].x, 34.0)
        self.assertEqual(operations[0].y, 0.0)
        self.assertEqual(operations[0].diameter, 15.0)
        self.assertEqual(operations[0].depth, 14.0)
        self.assertEqual(operations[0].face, "FRONT")

    def test_converts_8mm_minifix_axis_x_hole_to_edgedrill(self):
        from domain.anchors import MountFace
        from domain.hardware_library import HoleSpec
        from domain.manufacturing_ops import EdgeDrill
        from manufacturing.hardware_operation_adapter import (
            HardwareOperationAdapter,
        )

        hole = HoleSpec(
            diameter=8.0,
            depth=34.0,
            face=MountFace.LEFT,
            axis="X",
            offset_x=0.0,
            offset_y=0.0,
        )

        operations = HardwareOperationAdapter.to_unified([hole])

        self.assertEqual(len(operations), 1)
        self.assertIsInstance(operations[0], EdgeDrill)
        self.assertEqual(operations[0].x, 0.0)
        self.assertEqual(operations[0].z, 0.0)
        self.assertEqual(operations[0].diameter, 8.0)
        self.assertEqual(operations[0].depth, 34.0)
        self.assertEqual(operations[0].edge, "LEFT")

    def test_preserves_diameter_depth_face_edge(self):
        from domain.anchors import MountFace
        from domain.hardware_library import HoleSpec
        from manufacturing.hardware_operation_adapter import (
            HardwareOperationAdapter,
        )

        face_hole = HoleSpec(
            diameter=5.0,
            depth=12.0,
            face=MountFace.FRONT,
            offset_x=10.0,
            offset_y=20.0,
        )
        edge_hole = HoleSpec(
            diameter=3.0,
            depth=9.0,
            face=MountFace.RIGHT,
            axis="X",
            offset_x=30.0,
            offset_y=40.0,
        )

        operations = HardwareOperationAdapter.to_unified([face_hole, edge_hole])

        self.assertEqual(operations[0].diameter, 5.0)
        self.assertEqual(operations[0].depth, 12.0)
        self.assertEqual(operations[0].face, "FRONT")
        self.assertEqual(operations[1].diameter, 3.0)
        self.assertEqual(operations[1].depth, 9.0)
        self.assertEqual(operations[1].edge, "RIGHT")

    def test_handles_empty_hole_list(self):
        from manufacturing.hardware_operation_adapter import (
            HardwareOperationAdapter,
        )

        self.assertEqual(HardwareOperationAdapter.to_unified([]), [])

    def test_does_not_mutate_inputs(self):
        from domain.anchors import MountFace
        from domain.hardware_library import HoleSpec
        from manufacturing.hardware_operation_adapter import (
            HardwareOperationAdapter,
        )

        holes = [
            HoleSpec(
                diameter=15.0,
                depth=14.0,
                face=MountFace.FRONT,
                offset_x=34.0,
                offset_y=0.0,
            ),
            HoleSpec(
                diameter=8.0,
                depth=34.0,
                face=MountFace.LEFT,
                axis="X",
                offset_x=0.0,
                offset_y=0.0,
            ),
        ]
        snapshot = [hole.__dict__.copy() for hole in holes]

        HardwareOperationAdapter.to_unified(holes)

        self.assertEqual([hole.__dict__ for hole in holes], snapshot)


if __name__ == "__main__":
    unittest.main()
