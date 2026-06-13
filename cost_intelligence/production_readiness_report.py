from dataclasses import dataclass, field


@dataclass
class ProductionReadinessReport:
    status: str = "BLOCKED"
    manufacturing_ready: bool = False
    cost_risk_level: str = "LOW"
    nesting_risk_level: str = "LOW"
    profitability_ok: bool = False
    blocking_issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
