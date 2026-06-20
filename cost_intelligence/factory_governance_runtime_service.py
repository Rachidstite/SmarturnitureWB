from cost_intelligence.factory_governance_decision_report import (
    FactoryGovernanceDecisionReport,
)
from cost_intelligence.factory_governance_authority_report import (
    FactoryGovernanceAuthorityReport,
)
from cost_intelligence.factory_governance_policy_builder import (
    FactoryGovernancePolicyBuilder,
)
from cost_intelligence.factory_governance_policy_context import (
    FactoryGovernancePolicyContext,
)
from cost_intelligence.factory_governance_recommendation_builder import (
    FactoryGovernanceRecommendationBuilder,
)
from cost_intelligence.legacy_three_state_adapter import LegacyThreeStateAdapter


class FactoryGovernanceRuntimeService:

    _BUSINESS_CONSEQUENCES = {
        "APPROVED": "Proceed to production release",
        "REPRICE": "Adjust price before release",
        "SCHEDULE_LATER": "Delay execution until capacity clears",
        "REVIEW_REQUIRED": "Hold for human review",
        "REJECTED": "Stop release and do not manufacture",
    }

    def build(self, context: FactoryGovernancePolicyContext):
        policy_report = FactoryGovernancePolicyBuilder().build(context)
        recommendation_report = FactoryGovernanceRecommendationBuilder().build(
            policy_report,
            FactoryGovernanceAuthorityReport(),
        )
        legacy_decision_status = LegacyThreeStateAdapter().adapt(
            policy_report.governance_state
        )
        report = FactoryGovernanceDecisionReport(
            governance_state=policy_report.governance_state,
            legacy_decision_status=legacy_decision_status,
            reason_code=policy_report.reason_code,
            dominant_authority=policy_report.dominant_authority,
            owner=policy_report.dominant_authority,
            business_consequence=self._BUSINESS_CONSEQUENCES[
                policy_report.governance_state
            ],
            recommendations=self._build_recommendations(recommendation_report),
            warnings=list(recommendation_report.warnings),
        )
        report.explanation = policy_report.explanation
        report.primary_recommendation = (
            recommendation_report.primary_recommendation
        )
        report.secondary_recommendations = (
            recommendation_report.secondary_recommendations
        )
        return report

    @staticmethod
    def _build_recommendations(recommendation_report):
        recommendations = []
        if recommendation_report.primary_recommendation:
            recommendations.append(recommendation_report.primary_recommendation)
        recommendations.extend(
            list(recommendation_report.secondary_recommendations)
        )
        return recommendations
