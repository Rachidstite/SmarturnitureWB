from dataclasses import dataclass, field


@dataclass
class FactoryBottleneckRecommendationReport:
    bottleneck: str = ""
    severity: str = "LOW"
    primary_recommendation: str = "No bottleneck detected"
    secondary_recommendations: list = field(default_factory=list)
    expected_impact: str = "No immediate action required"
