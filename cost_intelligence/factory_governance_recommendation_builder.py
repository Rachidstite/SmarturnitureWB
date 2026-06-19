from cost_intelligence.factory_governance_recommendation_report import (
    FactoryGovernanceRecommendationReport,
)


class FactoryGovernanceRecommendationBuilder:

    _RECOMMENDATIONS = {
        "READINESS_BLOCKED": {
            "primary_recommendation": "Review manufacturing constraints",
            "secondary_recommendations": [
                "Review joinery validation",
                "Review collision validation",
            ],
            "urgency": "HIGH",
            "business_impact": "Blocking production release until readiness issues are cleared",
            "expected_outcome": "Resolve readiness issues before release",
        },
        "LOW_MARGIN": {
            "primary_recommendation": "Increase quotation price",
            "secondary_recommendations": [
                "Reduce material waste",
                "Review hardware selection",
            ],
            "urgency": "HIGH",
            "business_impact": "Commercial terms are weak and need repricing",
            "expected_outcome": "Improve margin before approval",
        },
        "OVER_CAPACITY": {
            "primary_recommendation": "Delay production start",
            "secondary_recommendations": [
                "Reschedule workload",
                "Increase production window",
            ],
            "urgency": "MEDIUM",
            "business_impact": "Factory capacity must clear before release",
            "expected_outcome": "Schedule the job when capacity is available",
        },
        "HIGH_LOAD": {
            "primary_recommendation": "Balance workload",
            "secondary_recommendations": [
                "Reassign production resources",
            ],
            "urgency": "MEDIUM",
            "business_impact": "Production load should be redistributed",
            "expected_outcome": "Reduce workload pressure before release",
        },
        "HIGH_RISK": {
            "primary_recommendation": "Manual engineering review",
            "secondary_recommendations": [
                "Review manufacturing feasibility",
            ],
            "urgency": "HIGH",
            "business_impact": "High-risk jobs require feasibility review",
            "expected_outcome": "Confirm the design can be manufactured safely",
        },
        "POLICY_CLEAR": {
            "primary_recommendation": "Proceed with production",
            "secondary_recommendations": [],
            "urgency": "LOW",
            "business_impact": "Job is ready for execution",
            "expected_outcome": "Release the job to production",
        },
    }

    def build(self, policy_report, authority_report):
        signal = authority_report.winning_signal or policy_report.reason_code
        payload = self._RECOMMENDATIONS.get(signal, self._RECOMMENDATIONS["POLICY_CLEAR"])
        warnings = []
        warnings.extend(list(policy_report.warnings))
        warnings.extend(list(authority_report.warnings))
        return FactoryGovernanceRecommendationReport(
            primary_recommendation=payload["primary_recommendation"],
            secondary_recommendations=list(payload["secondary_recommendations"]),
            urgency=payload["urgency"],
            business_impact=payload["business_impact"],
            expected_outcome=payload["expected_outcome"],
            warnings=warnings,
        )
