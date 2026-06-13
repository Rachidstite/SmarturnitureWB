from dataclasses import dataclass, field


@dataclass
class ManufacturingCostInsights:
    insights: list = field(default_factory=list)
    risk_level: str = "LOW"
    warnings: list = field(default_factory=list)
