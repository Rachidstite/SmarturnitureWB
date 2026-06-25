from project_engineering.available_operational_clearance_fact import (
    AvailableOperationalClearanceFact,
)


def extract_available_operational_clearance_fact(
    component_id: str,
    available_clearance_mm: float,
    direction: str = "",
    source: str = "",
) -> AvailableOperationalClearanceFact:
    return AvailableOperationalClearanceFact(
        component_id=component_id,
        available_clearance_mm=available_clearance_mm,
        direction=direction,
        source=source,
    )
