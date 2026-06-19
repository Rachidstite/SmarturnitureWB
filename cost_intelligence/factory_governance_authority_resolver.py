from cost_intelligence.factory_governance_authority_report import (
    FactoryGovernanceAuthorityReport,
)
from cost_intelligence.factory_governance_policy_context import (
    FactoryGovernancePolicyContext,
)


class FactoryGovernanceAuthorityResolver:

    def resolve(self, context: FactoryGovernancePolicyContext):
        active_signals = []
        if context.readiness_status == "BLOCKED":
            active_signals.append(
                (
                    1,
                    "ProductionReadinessBuilder",
                    "Hard fail release gate",
                    "READINESS_BLOCKED",
                )
            )
        if context.profitability_status == "LOW":
            active_signals.append(
                (
                    2,
                    "ProfitabilityCalculator",
                    "Commercial re-quote policy",
                    "LOW_MARGIN",
                )
            )
        if context.capacity_status == "OVERLOADED":
            active_signals.append(
                (
                    3,
                    "FactoryCapacityIntelligenceBuilder",
                    "Capacity authority",
                    "OVER_CAPACITY",
                )
            )
        if context.load_status == "HIGH":
            active_signals.append(
                (
                    4,
                    "FactoryLoadBuilder",
                    "Load authority",
                    "HIGH_LOAD",
                )
            )
        if context.risk_status == "HIGH":
            active_signals.append(
                (
                    5,
                    "FactoryDecisionBuilder",
                    "Risk triage authority",
                    "HIGH_RISK",
                )
            )

        if active_signals:
            rank, owner, scope, winning_signal = sorted(
                active_signals, key=lambda item: item[0]
            )[0]
            losing_signals = [
                signal
                for _, _, _, signal in sorted(active_signals, key=lambda item: item[0])[1:]
            ]
            explanation = f"{owner} wins because it has the highest authority rank."
        else:
            rank = 6
            owner = "FactoryGovernancePolicyBuilder"
            scope = "Default policy clarity authority"
            winning_signal = "POLICY_CLEAR"
            losing_signals = []
            explanation = "No blocking or risk signals were active."

        return FactoryGovernanceAuthorityReport(
            authority_owner=owner,
            authority_rank=rank,
            authority_scope=scope,
            winning_signal=winning_signal,
            losing_signals=losing_signals,
            explanation=explanation,
        )
