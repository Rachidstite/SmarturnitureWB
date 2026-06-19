from cost_intelligence.factory_governance_policy_context import (
    FactoryGovernancePolicyContext,
)
from cost_intelligence.factory_governance_policy_report import (
    FactoryGovernancePolicyReport,
)


class FactoryGovernancePolicyBuilder:

    def build(self, context: FactoryGovernancePolicyContext):
        if context.readiness_status == "BLOCKED":
            governance_state = "REJECTED"
            dominant_authority = "ProductionReadinessBuilder"
            reason_code = "READINESS_BLOCKED"
            explanation = "Readiness gate is blocked."
        elif context.profitability_status == "LOW":
            governance_state = "REPRICE"
            dominant_authority = "ProfitabilityCalculator"
            reason_code = "LOW_MARGIN"
            explanation = "Profitability is below the policy threshold."
        elif context.capacity_status == "OVERLOADED":
            governance_state = "SCHEDULE_LATER"
            dominant_authority = "FactoryCapacityIntelligenceBuilder"
            reason_code = "OVER_CAPACITY"
            explanation = "Factory capacity is overloaded."
        elif context.load_status == "HIGH":
            governance_state = "SCHEDULE_LATER"
            dominant_authority = "FactoryLoadBuilder"
            reason_code = "HIGH_LOAD"
            explanation = "Factory load is high."
        elif context.risk_status == "HIGH":
            governance_state = "REVIEW_REQUIRED"
            dominant_authority = "FactoryDecisionBuilder"
            reason_code = "HIGH_RISK"
            explanation = "Risk is high and requires review."
        else:
            governance_state = "APPROVED"
            dominant_authority = "FactoryGovernancePolicyBuilder"
            reason_code = "POLICY_CLEAR"
            explanation = "Policy is clear."

        return FactoryGovernancePolicyReport(
            governance_state=governance_state,
            dominant_authority=dominant_authority,
            reason_code=reason_code,
            explanation=explanation,
        )
