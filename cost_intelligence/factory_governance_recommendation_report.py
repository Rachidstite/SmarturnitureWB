from dataclasses import dataclass, field


@dataclass
class FactoryGovernanceRecommendationReport:
    primary_recommendation: str = ""
    secondary_recommendations: list = field(default_factory=list)
    urgency: str = ""
    business_impact: str = ""
    expected_outcome: str = ""
    warnings: list = field(default_factory=list)
