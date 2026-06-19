from dataclasses import dataclass, field


@dataclass
class FactoryGovernancePolicyReport:
    governance_state: str = ""
    dominant_authority: str = ""
    reason_code: str = ""
    explanation: str = ""
    recommendations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
