from dataclasses import dataclass


@dataclass
class RequiredOperationalClearanceFact:
    component_id: str
    required_clearance_mm: float
    direction: str = ""
    purpose: str = ""
    source: str = ""
