from dataclasses import dataclass, field


@dataclass
class FactoryDecisionReport:
    decision_status: str = "BLOCKED"
    manufacturing_ready: bool = False
    profitability_ok: bool = False
    cost_risk_level: str = "LOW"
    waste_risk_level: str = "LOW"
    nesting_risk_level: str = "LOW"
    quotation_risk_level: str = "UNKNOWN"
    margin_status: str = "UNKNOWN"
    blocking_issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
