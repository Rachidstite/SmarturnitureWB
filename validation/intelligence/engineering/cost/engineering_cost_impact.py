from dataclasses import dataclass


@dataclass(frozen=True)
class EngineeringCostImpact:

    code: str

    material_sheets: float

    machining_minutes: int

    hardware_cost: float
