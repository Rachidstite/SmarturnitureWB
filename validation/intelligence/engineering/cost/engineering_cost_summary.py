from dataclasses import dataclass


@dataclass(frozen=True)
class EngineeringCostSummary:

    material_sheets: float

    machining_minutes: int

    hardware_cost: float
