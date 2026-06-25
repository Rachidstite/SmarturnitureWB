from project_engineering.motion_envelope_fact import MotionEnvelopeFact
from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
)


def extract_simple_door_swing_motion_envelope(
    closed_bounds: SceneNodeBoundsMeasurement,
    swing_depth_mm: float,
    direction: str = "front",
    source: str = "",
) -> MotionEnvelopeFact:
    if direction == "back":
        y_min = closed_bounds.y_min - swing_depth_mm
        y_max = closed_bounds.y_max
    else:
        y_min = closed_bounds.y_min
        y_max = closed_bounds.y_max + swing_depth_mm

    return MotionEnvelopeFact(
        component_id=closed_bounds.node_id,
        motion_type="door_swing",
        x_min=closed_bounds.x_min,
        y_min=y_min,
        z_min=closed_bounds.z_min,
        x_max=closed_bounds.x_max,
        y_max=y_max,
        z_max=closed_bounds.z_max,
        direction=direction,
        source=source,
    )
