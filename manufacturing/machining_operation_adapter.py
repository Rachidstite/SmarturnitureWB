from manufacturing.unified_manufacturing_operation import \
    UnifiedManufacturingOperation


class MachiningOperationAdapter:

    @staticmethod
    def from_operation(op):

        if hasattr(op, "local_x"):
            return UnifiedManufacturingOperation(
                operation_type=getattr(op, "op_type", ""),
                diameter=getattr(op, "diameter", 0.0),
                depth=getattr(op, "depth", 0.0),
                is_through=getattr(op, "is_through", False),
                face=getattr(op, "face", ""),
                x=getattr(op, "local_x", 0.0),
                y=getattr(op, "local_y", 0.0),
                axis=getattr(op, "axis", "Z"),
                source="modern-core",
                metadata={}
            )

        if hasattr(op, "transform"):
            transform = getattr(op, "transform")

            return UnifiedManufacturingOperation(
                operation_type=getattr(op, "op_type", ""),
                diameter=getattr(op, "diameter", 0.0),
                depth=getattr(op, "depth", 0.0),
                is_through=getattr(op, "is_through", False),
                x=getattr(transform, "x", 0.0),
                y=getattr(transform, "y", 0.0),
                z=getattr(transform, "z", 0.0),
                source="modern-hardware",
                metadata={}
            )

        raise TypeError(
            f"Unsupported operation type: {type(op)}"
        )
