from dataclasses import dataclass


@dataclass
class SceneNodeBoundsMeasurement:
    node_id: str
    x_min: float
    y_min: float
    z_min: float
    x_max: float
    y_max: float
    z_max: float
    source: str = ""


def measure_scene_node_bounds(node, source: str = "") -> SceneNodeBoundsMeasurement:
    node_id = ""

    identity = getattr(node, "identity", None)
    if identity is not None:
        node_id = getattr(identity, "key", "")
    if not node_id:
        node_id = getattr(node, "id", "") or ""

    x = float(getattr(node, "x", 0.0))
    y = float(getattr(node, "y", 0.0))
    z = float(getattr(node, "z", 0.0))
    width = float(getattr(node, "width", 0.0))
    depth = float(getattr(node, "depth", 0.0))
    height = float(getattr(node, "height", 0.0))

    return SceneNodeBoundsMeasurement(
        node_id=node_id,
        x_min=x,
        y_min=y,
        z_min=z,
        x_max=x + width,
        y_max=y + depth,
        z_max=z + height,
        source=source,
    )
