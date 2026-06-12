from dataclasses import dataclass, field


@dataclass
class ManufacturingCostRiskReport:
    risk_level: str = "LOW"
    findings: list = field(default_factory=list)
    recommendation: str = ""
    warnings: list = field(default_factory=list)
