from dataclasses import dataclass, field


@dataclass
class WasteIntelligenceReport:
    waste_ratio: float = 0.0
    waste_cost: float = 0.0
    recovery_score: int = 0
    risk_level: str = "LOW"
    recommendation: str = ""
    warnings: list = field(default_factory=list)
