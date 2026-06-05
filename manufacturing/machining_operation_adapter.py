from manufacturing.unified_manufacturing_operation import \
    UnifiedManufacturingOperation


class MachiningOperationAdapter:

    @staticmethod
    def from_modern_operation(op):

        return UnifiedManufacturingOperation(
            operation_type=getattr(op, "op_type", ""),

            diameter=getattr(op, "diameter", 0.0),

            depth=getattr(op, "depth", 0.0),

            face=getattr(op, "face", ""),

            x=getattr(op, "local_x", 0.0),

            y=getattr(op, "local_y", 0.0),

            axis=getattr(op, "axis", "Z"),

            source="modern",

            metadata={}
        )
