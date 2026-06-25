from project_engineering.motion_envelope_fact import MotionEnvelopeFact
from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
)


def extract_motion_envelope_from_bounds(
    bounds: SceneNodeBoundsMeasurement,
    motion_type: str = "",
    direction: str = "",
    source: str = "",
) -> MotionEnvelopeFact:
    return MotionEnvelopeFact(
        component_id=bounds.node_id,
        motion_type=motion_type,
        x_min=bounds.x_min,
        y_min=bounds.y_min,
        z_min=bounds.z_min,
        x_max=bounds.x_max,
        y_max=bounds.y_max,
        z_max=bounds.z_max,
        direction=direction,
        source=source,
    )
