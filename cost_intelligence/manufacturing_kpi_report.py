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
    project_profitability_status: str = "UNKNOWN"
    material_efficiency_status: str = "UNKNOWN"
    waste_risk_status: str = "UNKNOWN"
    bottleneck_status: str = "UNKNOWN"
    production_readiness_status: str = "UNKNOWN"
    overall_management_status: str = "UNKNOWN"
