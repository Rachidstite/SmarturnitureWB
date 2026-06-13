from cost_intelligence.offcut_intelligence_report import (
    OffcutIntelligenceReport,
)


class OffcutIntelligenceBuilder:

    def build(self, offcut_report):
        if offcut_report.total_offcuts == 0:
            return OffcutIntelligenceReport(
                recommendation="No offcuts available for reuse",
                warnings=offcut_report.warnings,
            )

        reuse_rate = offcut_report.reusable_offcuts / offcut_report.total_offcuts
        waste_recovery_score = int(reuse_rate * 100)

        if waste_recovery_score >= 70:
            recommendation = "Good offcut reuse potential"
        elif waste_recovery_score >= 40:
            recommendation = "Moderate offcut reuse potential"
        else:
            recommendation = "Low offcut reuse potential"

        return OffcutIntelligenceReport(
            reuse_rate=reuse_rate,
            waste_recovery_score=waste_recovery_score,
            recommendation=recommendation,
            warnings=offcut_report.warnings,
        )
