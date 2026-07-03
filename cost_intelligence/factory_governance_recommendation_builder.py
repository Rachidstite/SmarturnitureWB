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

    _MANAGEMENT_RECOMMENDATIONS = (
        (
            "production_readiness_status",
            ("READY_WITH_WARNINGS", "BLOCKED"),
            {
                "primary_recommendation": (
                    "Delay production release until readiness issues are cleared"
                ),
                "urgency": "HIGH",
                "business_impact": "Production should not start while readiness issues remain",
                "expected_outcome": "Clear readiness issues before releasing the job",
            },
        ),
        (
            "project_profitability_status",
            ("LOW", "CRITICAL"),
            {
                "primary_recommendation": "Review quotation pricing",
                "urgency": "HIGH",
                "business_impact": "Profitability is weak and needs commercial review",
                "expected_outcome": "Improve quote quality before approval",
            },
        ),
        (
            "bottleneck_status",
            ("HIGH",),
            {
                "primary_recommendation": "Reschedule production around bottlenecks",
                "urgency": "MEDIUM",
                "business_impact": "Factory bottlenecks may delay execution",
                "expected_outcome": "Reduce throughput pressure before release",
            },
        ),
        (
            "waste_risk_status",
            ("HIGH",),
            {
                "primary_recommendation": "Review nesting and material usage",
                "urgency": "HIGH",
                "business_impact": "Waste exposure is likely to erode project margin",
                "expected_outcome": "Reduce waste before production is approved",
            },
        ),
        (
            "material_efficiency_status",
            ("STABLE", "LOW", "INEFFICIENT"),
            {
                "primary_recommendation": "Review material efficiency before release",
                "urgency": "MEDIUM",
                "business_impact": "Material yield should improve to protect margin",
                "expected_outcome": "Increase material efficiency before approval",
            },
        ),
    )

    def build(self, policy_report, authority_report, management_status_source=None):
        signal = authority_report.winning_signal or policy_report.reason_code
        payload = self._RECOMMENDATIONS.get(
            signal,
            self._RECOMMENDATIONS["POLICY_CLEAR"],
        )
        management_recommendations = self._build_management_recommendations(
            management_status_source
        )

        if signal == "POLICY_CLEAR" and management_recommendations:
            primary = management_recommendations[0]
            payload = {
                "primary_recommendation": primary["primary_recommendation"],
                "secondary_recommendations": [
                    item["primary_recommendation"]
                    for item in management_recommendations[1:]
                ],
                "urgency": primary["urgency"],
                "business_impact": primary["business_impact"],
                "expected_outcome": primary["expected_outcome"],
            }
        else:
            payload = {
                "primary_recommendation": payload["primary_recommendation"],
                "secondary_recommendations": list(
                    payload["secondary_recommendations"]
                )
                + [
                    item["primary_recommendation"]
                    for item in management_recommendations
                ],
                "urgency": payload["urgency"],
                "business_impact": payload["business_impact"],
                "expected_outcome": payload["expected_outcome"],
            }

        warnings = []
        warnings.extend(list(policy_report.warnings))
        warnings.extend(list(authority_report.warnings))
        return FactoryGovernanceRecommendationReport(
            primary_recommendation=payload["primary_recommendation"],
            secondary_recommendations=self._dedupe_recommendations(
                payload["secondary_recommendations"]
            ),
            urgency=payload["urgency"],
            business_impact=payload["business_impact"],
            expected_outcome=payload["expected_outcome"],
            warnings=warnings,
        )

    @classmethod
    def _build_management_recommendations(cls, management_status_source):
        if management_status_source is None:
            return []

        recommendations = []
        for field_name, triggering_values, payload in cls._MANAGEMENT_RECOMMENDATIONS:
            field_value = getattr(
                management_status_source,
                field_name,
                "UNKNOWN",
            )
            if field_value in triggering_values:
                recommendations.append(payload)
        return recommendations

    @staticmethod
    def _dedupe_recommendations(recommendations):
        deduped = []
        seen = set()
        for recommendation in recommendations:
            if recommendation in seen:
                continue
            seen.add(recommendation)
            deduped.append(recommendation)
        return deduped
