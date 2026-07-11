from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class ManufacturingOperationAdapter:

    @staticmethod
    def to_unified(operation, *, panel_identity=""):
        if isinstance(operation, UnifiedManufacturingOperation):
            return operation

        operation_type = ManufacturingOperationAdapter._operation_type(
            operation
        )
        metadata = ManufacturingOperationAdapter._metadata(
            operation,
            panel_identity=panel_identity,
        )
        original_operation_type = (
            ManufacturingOperationAdapter._original_operation_type(operation)
        )
        if original_operation_type is not None and "original_operation_type" not in metadata:
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
            source=str(
                metadata.get("source_operation_reference")
                or operation.__class__.__name__
            ),
            metadata=metadata,
        )

    @staticmethod
    def to_unified_list(operations):
        return [
            ManufacturingOperationAdapter.to_unified(operation)
            for operation in operations
        ]

    @staticmethod
    def to_unified_panel_operations(panel_specs):
        unified_operations = []
        for panel in panel_specs or []:
            panel_identity = str(getattr(panel, "identity", "") or "").strip()
            for operation in getattr(panel, "cnc_operations", ()) or ():
                unified_operations.append(
                    ManufacturingOperationAdapter.to_unified(
                        operation,
                        panel_identity=panel_identity,
                    )
                )
        return unified_operations

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

    @staticmethod
    def _metadata(operation, *, panel_identity=""):
        metadata = dict(getattr(operation, "metadata", None) or {})
        if panel_identity and not str(metadata.get("panel_identity", "") or "").strip():
            metadata["panel_identity"] = panel_identity
        return metadata
