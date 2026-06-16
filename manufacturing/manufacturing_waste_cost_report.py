from dataclasses import dataclass, field


@dataclass
class ManufacturingWasteCostReport:
    waste_area_m2: float = 0.0
    estimated_waste_cost: float = 0.0
    sheet_cost: float = 0.0
    warnings: list = field(default_factory=list)
