from dataclasses import dataclass, field


@dataclass
class ManufacturingCostReport:
    material_cost: float = 0.0
    edge_banding_cost: float = 0.0
    drilling_cost: float = 0.0
    hardware_cost: float = 0.0
    complexity_cost: float = 0.0
    panel_handling_cost: float = 0.0
    cnc_labor_cost: float = 0.0
    drilling_labor_cost: float = 0.0
    edge_banding_labor_cost: float = 0.0
    assembly_labor_cost: float = 0.0
    total_labor_cost: float = 0.0
    overhead_cost: float = 0.0
    total_manufacturing_cost: float = 0.0
    currency: str = "MAD"
    warnings: list = field(default_factory=list)
