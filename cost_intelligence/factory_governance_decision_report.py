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

    @property
    def explanation(self):
        return getattr(self, "_explanation", "")

    @explanation.setter
    def explanation(self, value):
        self._explanation = value

    @property
    def primary_recommendation(self):
        return getattr(self, "_primary_recommendation", "")

    @primary_recommendation.setter
    def primary_recommendation(self, value):
        self._primary_recommendation = value

    @property
    def secondary_recommendations(self):
        return getattr(self, "_secondary_recommendations", [])

    @secondary_recommendations.setter
    def secondary_recommendations(self, value):
        self._secondary_recommendations = list(value)

    @property
    def manufacturing_recommendation(self):
        return getattr(self, "_manufacturing_recommendation", "")

    @manufacturing_recommendation.setter
    def manufacturing_recommendation(self, value):
        self._manufacturing_recommendation = value

    @property
    def manufacturing_secondary_recommendations(self):
        return getattr(self, "_manufacturing_secondary_recommendations", [])

    @manufacturing_secondary_recommendations.setter
    def manufacturing_secondary_recommendations(self, value):
        self._manufacturing_secondary_recommendations = list(value)
