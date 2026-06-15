from cost_intelligence.offcut_intelligence_report import (
    OffcutIntelligenceReport,
)


class OffcutIntelligenceBuilder:

    def build(self, offcut_report, price_per_m2=0.0):
        reusable_areas = [
            offcut.area
            for offcut in offcut_report.offcuts
            if offcut.reusable
        ]
        reusable_area = sum(reusable_areas)
        largest_reusable_area = max(reusable_areas, default=0.0)
        estimated_recovered_value = (
            reusable_area
            / 1_000_000
            * price_per_m2
        )

        if offcut_report.total_offcuts == 0:
            return OffcutIntelligenceReport(
                recommendation="No offcuts available for reuse",
                warnings=offcut_report.warnings,
                reusable_area=reusable_area,
                largest_reusable_area=largest_reusable_area,
                estimated_recovered_value=estimated_recovered_value,
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
            reusable_area=reusable_area,
            largest_reusable_area=largest_reusable_area,
            estimated_recovered_value=estimated_recovered_value,
        )
