from domain.manufacturing_ops import (
    FaceDrill,
    EdgeDrill,
    Groove
)

from manufacturing.unified_manufacturing_operation import \
    UnifiedManufacturingOperation


class LegacyOperationAdapter:

    @staticmethod
    def from_operation(op):

        if isinstance(op, FaceDrill):
            return UnifiedManufacturingOperation(
                operation_type="FACE_DRILL",
                diameter=op.diameter,
                depth=op.depth,
                x=op.x,
                y=op.y,
                face=op.face,
                source="legacy",
                metadata={}
            )

        if isinstance(op, EdgeDrill):
            return UnifiedManufacturingOperation(
                operation_type="EDGE_DRILL",
                diameter=op.diameter,
                depth=op.depth,
                x=op.x,
                z=op.z,
                face=op.edge,
                source="legacy",
                metadata={}
            )

        if isinstance(op, Groove):
            return UnifiedManufacturingOperation(
                operation_type="GROOVE",
                depth=op.depth,
                x=op.start_x,
                y=op.start_y,
                face=op.face,
                source="legacy",
                metadata={
                    "width": op.width,
                    "length": op.length
                }
            )

        raise TypeError(
            f"Unsupported legacy operation: {type(op)}"
        )
