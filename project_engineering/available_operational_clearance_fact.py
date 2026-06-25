from dataclasses import dataclass


@dataclass
class AvailableOperationalClearanceFact:
    component_id: str
    available_clearance_mm: float
    direction: str = ""
    source: str = ""
