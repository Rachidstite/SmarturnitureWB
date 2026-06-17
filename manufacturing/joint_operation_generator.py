from copy import deepcopy

from domain.manufacturing_ops import FaceDrill, EdgeDrill
from manufacturing.hardware_operation_adapter import (
    HardwareOperationAdapter,
)

class JointOperationGenerator:

    @staticmethod
    def minifix_joint(parent_node, child_node):

        ops = []

        # Cam 15mm
        ops.append(
            FaceDrill(
                x=34,
                y=64,
                diameter=15,
                depth=12,
                face="TOP"
            )
        )

        # Dowel hole
        ops.append(
            EdgeDrill(
                x=64,
                z=(parent_node.thickness / 2),
                diameter=8,
                depth=30,
                edge="TOP"
            )
        )

        return ops

    @staticmethod
    def minifix_joint_from_hardware(parent_node, child_node, hardware_spec):
        return HardwareOperationAdapter.to_unified(
            deepcopy(hardware_spec.target_holes)
        )
