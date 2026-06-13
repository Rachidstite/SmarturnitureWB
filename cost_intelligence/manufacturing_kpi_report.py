from dataclasses import dataclass, field


@dataclass
class ManufacturingKPIReport:
    total_manufacturing_cost: float = 0.0
    gross_margin_rate: float = 0.0
    utilization_rate: float = 0.0
    waste_rate: float = 0.0
    reuse_rate: float = 0.0
    production_status: str = ""
    warnings: list = field(default_factory=list)
