from cost_intelligence.factory_governance_commercial_impact_report import (
    FactoryGovernanceCommercialImpactReport,
)


class FactoryGovernanceCommercialImpactBuilder:

    _RECOMMENDATION_SIGNAL_MAP = {
        "Review manufacturing constraints": "READINESS_BLOCKED",
        "Increase quotation price": "LOW_MARGIN",
        "Delay production start": "OVER_CAPACITY",
        "Balance workload": "HIGH_LOAD",
        "Manual engineering review": "HIGH_RISK",
        "Proceed with production": "POLICY_CLEAR",
    }

    def build(self, recommendation_report, quotation_report, profitability_report):
        if not recommendation_report.primary_recommendation:
            return FactoryGovernanceCommercialImpactReport()

        signal = self._RECOMMENDATION_SIGNAL_MAP.get(
            recommendation_report.primary_recommendation,
            "POLICY_CLEAR",
        )

        if signal == "LOW_MARGIN":
            estimated_margin_improvement = max(
                0.0, 0.15 - profitability_report.gross_margin_rate
            )
            estimated_cost_reduction = (
                quotation_report.production_cost * estimated_margin_improvement
            )
            estimated_profit_increase = estimated_cost_reduction
            impact_confidence = 0.90
            impact_explanation = (
                "Margin recovery opportunity based on the current profitability "
                f"rate of {profitability_report.gross_margin_rate:.2%}."
            )
        elif signal == "OVER_CAPACITY":
            estimated_margin_improvement = 0.0
            estimated_cost_reduction = quotation_report.production_cost * 0.05
            estimated_profit_increase = estimated_cost_reduction
            impact_confidence = 0.70
            impact_explanation = (
                "Schedule improvement opportunity can reduce execution pressure."
            )
        elif signal == "HIGH_LOAD":
            estimated_margin_improvement = 0.0
            estimated_cost_reduction = quotation_report.production_cost * 0.03
            estimated_profit_increase = estimated_cost_reduction
            impact_confidence = 0.65
            impact_explanation = (
                "Productivity improvement opportunity can rebalance workload."
            )
        elif signal == "HIGH_RISK":
            estimated_margin_improvement = 0.0
            estimated_cost_reduction = quotation_report.production_cost * 0.02
            estimated_profit_increase = estimated_cost_reduction
            impact_confidence = 0.60
            impact_explanation = (
                "Risk reduction opportunity can prevent downstream rework."
            )
        elif signal == "READINESS_BLOCKED":
            estimated_margin_improvement = 0.0
            estimated_cost_reduction = 0.0
            estimated_profit_increase = 0.0
            impact_confidence = 0.85
            impact_explanation = (
                "Readiness recovery can unlock the commercial opportunity."
            )
        else:
            estimated_margin_improvement = 0.0
            estimated_cost_reduction = 0.0
            estimated_profit_increase = 0.0
            impact_confidence = 1.0
            impact_explanation = "No commercial action required."

        return FactoryGovernanceCommercialImpactReport(
            estimated_margin_improvement=estimated_margin_improvement,
            estimated_cost_reduction=estimated_cost_reduction,
            estimated_profit_increase=estimated_profit_increase,
            impact_confidence=impact_confidence,
            impact_explanation=impact_explanation,
        )
