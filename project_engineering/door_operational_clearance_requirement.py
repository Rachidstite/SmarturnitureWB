from project_engineering.required_operational_clearance_fact import (
    RequiredOperationalClearanceFact,
)


def build_door_required_operational_clearance_fact(
    door_id: str,
    required_clearance_mm: float,
    direction: str = "front",
    source: str = "",
) -> RequiredOperationalClearanceFact:
    return RequiredOperationalClearanceFact(
        component_id=door_id,
        required_clearance_mm=required_clearance_mm,
        direction=direction,
        purpose="door operation",
        source=source,
    )
