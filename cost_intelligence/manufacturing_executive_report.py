from dataclasses import dataclass, field


@dataclass
class ManufacturingExecutiveReport:
    overall_score: int = 0
    overall_grade: str = "F"
    production_status: str = ""
    total_manufacturing_cost: float = 0.0
    gross_margin_rate: float = 0.0
    utilization_rate: float = 0.0
    waste_rate: float = 0.0
    engineering_complexity: str = "LOW"
    estimated_engineering_minutes: float = 0.0
    recovery_score: int = 0
    governance_state: str = ""
    legacy_decision_status: str = ""
    dominant_authority: str = ""
    reason_code: str = ""
    warnings: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)

    @property
    def governance_explanation(self):
        return getattr(self, "_governance_explanation", "")

    @governance_explanation.setter
    def governance_explanation(self, value):
        self._governance_explanation = value

    @property
    def governance_primary_recommendation(self):
        return getattr(self, "_governance_primary_recommendation", "")

    @governance_primary_recommendation.setter
    def governance_primary_recommendation(self, value):
        self._governance_primary_recommendation = value

    @property
    def governance_secondary_recommendations(self):
        return getattr(self, "_governance_secondary_recommendations", [])

    @governance_secondary_recommendations.setter
    def governance_secondary_recommendations(self, value):
        self._governance_secondary_recommendations = list(value)

    @property
    def governance_manufacturing_recommendation(self):
        return getattr(self, "_governance_manufacturing_recommendation", "")

    @governance_manufacturing_recommendation.setter
    def governance_manufacturing_recommendation(self, value):
        self._governance_manufacturing_recommendation = value

    @property
    def governance_manufacturing_secondary_recommendations(self):
        return getattr(
            self,
            "_governance_manufacturing_secondary_recommendations",
            [],
        )

    @governance_manufacturing_secondary_recommendations.setter
    def governance_manufacturing_secondary_recommendations(self, value):
        self._governance_manufacturing_secondary_recommendations = list(value)
