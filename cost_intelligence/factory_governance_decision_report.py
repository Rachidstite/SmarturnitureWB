from dataclasses import dataclass, field


@dataclass
class FactoryGovernanceDecisionReport:
    governance_state: str = "REVIEW_REQUIRED"
    legacy_decision_status: str = "REVIEW_REQUIRED"
    reason_code: str = ""
    dominant_authority: str = ""
    owner: str = ""
    business_consequence: str = ""
    recommendations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
