from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class ManufacturingOperationAdapter:

    @staticmethod
    def to_unified(operation):
        if isinstance(operation, UnifiedManufacturingOperation):
            return operation

        operation_type = ManufacturingOperationAdapter._operation_type(
            operation
        )
        metadata = {}
        original_operation_type = (
            ManufacturingOperationAdapter._original_operation_type(operation)
        )
        if original_operation_type is not None:
            metadata["original_operation_type"] = original_operation_type

        return UnifiedManufacturingOperation(
            operation_type=operation_type,
            diameter=getattr(operation, "diameter", 0.0),
            depth=getattr(operation, "depth", 0.0),
            is_through=getattr(operation, "is_through", False),
            x=ManufacturingOperationAdapter._coordinate(operation, "local_x", "x"),
            y=ManufacturingOperationAdapter._coordinate(operation, "local_y", "y"),
            z=getattr(operation, "z", 0.0),
            face=getattr(operation, "face", ""),
            axis=getattr(operation, "axis", "Z"),
            source=operation.__class__.__name__,
            metadata=metadata,
        )

    @staticmethod
    def to_unified_list(operations):
        return [
            ManufacturingOperationAdapter.to_unified(operation)
            for operation in operations
        ]

    @staticmethod
    def _operation_type(operation):
        if hasattr(operation, "op_type"):
            return operation.op_type
        if hasattr(operation, "operation_type"):
            return operation.operation_type

        class_name = operation.__class__.__name__
        if class_name in ("FaceDrill", "EdgeDrill"):
            return "DRILL"
        if class_name == "Groove":
            return "GROOVE"

        return "UNKNOWN"

    @staticmethod
    def _original_operation_type(operation):
        if hasattr(operation, "op_type"):
            return operation.op_type
        if hasattr(operation, "operation_type"):
            return operation.operation_type

        return None

    @staticmethod
    def _coordinate(operation, local_name, absolute_name):
        if hasattr(operation, local_name):
            return getattr(operation, local_name)

        return getattr(operation, absolute_name, 0.0)
