from project_engineering.required_operational_clearance_fact import (
    RequiredOperationalClearanceFact,
)


def extract_required_operational_clearance_fact(
    component_id: str,
    required_clearance_mm: float,
    direction: str = "",
    purpose: str = "",
    source: str = "",
) -> RequiredOperationalClearanceFact:
    return RequiredOperationalClearanceFact(
        component_id=component_id,
        required_clearance_mm=required_clearance_mm,
        direction=direction,
        purpose=purpose,
        source=source,
    )
