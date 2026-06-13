from cost_intelligence.waste_intelligence_report import WasteIntelligenceReport


class WasteIntelligenceBuilder:

    def build(
        self,
        consumption_report,
        cost_estimate,
        offcut_intelligence_report=None,
    ):
        recovery_score = (
            offcut_intelligence_report.waste_recovery_score
            if offcut_intelligence_report
            else 0
        )

        if consumption_report.waste_ratio >= 0.30 and recovery_score < 40:
            risk_level = "HIGH"
            recommendation = "High waste risk: improve nesting or reuse policy"
        elif consumption_report.waste_ratio >= 0.15:
            risk_level = "MEDIUM"
            recommendation = "Moderate waste risk: review sheet utilization"
        else:
            risk_level = "LOW"
            recommendation = "Waste level acceptable"

        warnings = list(consumption_report.warnings)
        warnings.extend(cost_estimate.warnings)
        if offcut_intelligence_report:
            warnings.extend(offcut_intelligence_report.warnings)

        return WasteIntelligenceReport(
            waste_ratio=consumption_report.waste_ratio,
            waste_cost=cost_estimate.waste_cost,
            recovery_score=recovery_score,
            risk_level=risk_level,
            recommendation=recommendation,
            warnings=warnings,
        )
