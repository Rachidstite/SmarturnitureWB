from dataclasses import dataclass, field


@dataclass
class FurnitureProjectExecutiveReport:
    total_cabinets: int = 0
    total_physical_parts: int = 0
    total_machining_operations: int = 0
    overall_score: int = 0
    overall_grade: str = "F"
    decision_status: str = "BLOCKED"
    production_status: str = ""
    total_manufacturing_cost: float = 0.0
    gross_margin_rate: float = 0.0
    utilization_rate: float = 0.0
    waste_rate: float = 0.0
    recovery_score: int = 0
    warnings: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
    project_profitability_status: str = "UNKNOWN"
    material_efficiency_status: str = "UNKNOWN"
    waste_risk_status: str = "UNKNOWN"
    bottleneck_status: str = "UNKNOWN"
    production_readiness_status: str = "UNKNOWN"
    overall_management_status: str = "UNKNOWN"
