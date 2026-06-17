from dataclasses import dataclass, field


@dataclass
class LaborCostReport:
    cnc_labor_cost: float = 0.0
    drilling_labor_cost: float = 0.0
    edge_banding_labor_cost: float = 0.0
    assembly_labor_cost: float = 0.0
    total_labor_cost: float = 0.0
    currency: str = "MAD"
    warnings: list = field(default_factory=list)
