from manufacturing.canonical_cnc_row import CanonicalCNCRow


class CanonicalCNCMapper:

    @staticmethod
    def from_unified_operation(panel_spec, operation):
        return CanonicalCNCRow(
            panel_id=panel_spec.identity,
            panel_role=str(panel_spec.role),
            operation_type=operation.operation_type,
            face=operation.face,
            axis=operation.axis,
            x=operation.x,
            y=operation.y,
            z=operation.z,
            diameter=operation.diameter,
            depth=operation.depth,
            is_through=operation.is_through,
            source=operation.source,
        )
