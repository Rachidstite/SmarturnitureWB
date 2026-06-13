from cost_intelligence.nesting_intelligence_report import (
    NestingIntelligenceReport,
)


class NestingIntelligenceBuilder:

    def build(
        self,
        sheet_utilization_report,
        offcut_intelligence_report,
        waste_intelligence_report,
    ):
        if waste_intelligence_report.risk_level == "HIGH":
            risk_level = "HIGH"
            recommendation = (
                "Improve nesting efficiency and offcut reuse before production"
            )
        elif sheet_utilization_report.utilization_rate < 0.60:
            risk_level = "MEDIUM"
            recommendation = "Review nesting layout for better sheet utilization"
        else:
            risk_level = "LOW"
            recommendation = "Nesting quality acceptable"

        warnings = list(sheet_utilization_report.warnings)
        warnings.extend(offcut_intelligence_report.warnings)
        warnings.extend(waste_intelligence_report.warnings)

        return NestingIntelligenceReport(
            utilization_rate=sheet_utilization_report.utilization_rate,
            waste_rate=sheet_utilization_report.waste_rate,
            recovery_score=offcut_intelligence_report.waste_recovery_score,
            risk_level=risk_level,
            recommendation=recommendation,
            warnings=warnings,
        )
