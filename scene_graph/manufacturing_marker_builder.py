from scene_graph.manufacturing_marker import ManufacturingMarker


class ManufacturingMarkerBuilder:
    VISUAL_TYPE_BY_OPERATION_TYPE = {
        "GROOVE": "SLOT",
        "MINIFIX": "CIRCLE",
        "CONFIRMAT": "CIRCLE",
        "DOWEL": "CIRCLE",
        "SHELF_PIN": "POINT",
    }

    @staticmethod
    def build(node, operations):
        if not operations:
            return []

        target_node_id = ManufacturingMarkerBuilder._target_node_id(node)
        markers = []

        for operation in operations:
            operation_type = ManufacturingMarkerBuilder._operation_type(operation)
            markers.append(
                ManufacturingMarker(
                    operation_type=operation_type,
                    target_node_id=target_node_id,
                    visual_type=ManufacturingMarkerBuilder._visual_type(
                        operation_type
                    ),
                    start_x=ManufacturingMarkerBuilder._coordinate(
                        operation, "start_x", "x"
                    ),
                    start_y=ManufacturingMarkerBuilder._coordinate(
                        operation, "start_y", "y"
                    ),
                    width=getattr(operation, "width", 0.0),
                    depth=getattr(operation, "depth", 0.0),
                    length=getattr(operation, "length", 0.0),
                    face=getattr(operation, "face", ""),
                    metadata=ManufacturingMarkerBuilder._metadata(operation),
                )
            )

        return markers

    @staticmethod
    def _target_node_id(node):
        identity = getattr(node, "identity", None)
        if hasattr(identity, "key"):
            return identity.key
        return str(identity or "")

    @staticmethod
    def _operation_type(operation):
        for attr in ("operation_type", "op_type"):
            value = getattr(operation, attr, None)
            if value:
                return value

        return operation.__class__.__name__.upper()

    @staticmethod
    def _visual_type(operation_type):
        return ManufacturingMarkerBuilder.VISUAL_TYPE_BY_OPERATION_TYPE.get(
            operation_type,
            "ANNOTATION",
        )

    @staticmethod
    def _coordinate(operation, preferred_name, fallback_name):
        if hasattr(operation, preferred_name):
            return getattr(operation, preferred_name)
        return getattr(operation, fallback_name, 0.0)

    @staticmethod
    def _metadata(operation):
        metadata = getattr(operation, "metadata", None)
        if isinstance(metadata, dict):
            return dict(metadata)
        return {}
