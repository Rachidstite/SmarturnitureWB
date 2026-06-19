from dataclasses import dataclass, field


@dataclass
class ManufacturingExecutiveReport:
    overall_score: int = 0
    overall_grade: str = "F"
    production_status: str = ""
    total_manufacturing_cost: float = 0.0
    gross_margin_rate: float = 0.0
    utilization_rate: float = 0.0
    waste_rate: float = 0.0
    recovery_score: int = 0
    governance_state: str = ""
    legacy_decision_status: str = ""
    dominant_authority: str = ""
    reason_code: str = ""
    warnings: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
