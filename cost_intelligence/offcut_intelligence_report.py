from dataclasses import dataclass, field


@dataclass
class OffcutIntelligenceReport:
    reuse_rate: float = 0.0
    waste_recovery_score: int = 0
    recommendation: str = ""
    warnings: list = field(default_factory=list)
