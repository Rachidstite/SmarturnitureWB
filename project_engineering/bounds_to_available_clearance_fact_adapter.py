from project_engineering.available_operational_clearance_fact import (
    AvailableOperationalClearanceFact,
)
from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
)


def build_available_clearance_fact_from_bounds_measurement(
    bounds,
    available_clearance_mm: float,
    direction: str = "",
    source: str = "",
) -> AvailableOperationalClearanceFact:
    return AvailableOperationalClearanceFact(
        component_id=getattr(bounds, "node_id", ""),
        available_clearance_mm=available_clearance_mm,
        direction=direction,
        source=source,
    )
