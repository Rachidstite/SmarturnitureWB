from cost_intelligence.waste_intelligence_report import WasteIntelligenceReport


class WasteIntelligenceBuilder:

    def build(
        self,
        consumption_report,
        cost_estimate,
        offcut_intelligence_report=None,
    ):
        sheet_utilization_report = getattr(
            self,
            "sheet_utilization_report",
            None,
        )
        waste_ratio = getattr(consumption_report, "waste_ratio", None)
        if waste_ratio is None:
            waste_ratio = getattr(
                sheet_utilization_report,
                "waste_rate",
                0.0,
            )

        recovery_score = (
            offcut_intelligence_report.waste_recovery_score
            if offcut_intelligence_report
            else 0
        )

        if waste_ratio >= 0.30 and recovery_score < 40:
            risk_level = "HIGH"
            recommendation = "High waste risk: improve nesting or reuse policy"
        elif waste_ratio >= 0.15:
            risk_level = "MEDIUM"
            recommendation = "Moderate waste risk: review sheet utilization"
        else:
            risk_level = "LOW"
            recommendation = "Waste level acceptable"

        warnings = list(consumption_report.warnings)
        warnings.extend(cost_estimate.warnings)
        if sheet_utilization_report:
            warnings.extend(getattr(sheet_utilization_report, "warnings", []) or [])
        if offcut_intelligence_report:
            warnings.extend(offcut_intelligence_report.warnings)

        reuse_rate = (
            offcut_intelligence_report.reuse_rate
            if offcut_intelligence_report
            else 0.0
        )
        reusable_area = (
            offcut_intelligence_report.reusable_area
            if offcut_intelligence_report
            else 0.0
        )
        largest_reusable_area = (
            offcut_intelligence_report.largest_reusable_area
            if offcut_intelligence_report
            else 0.0
        )
        estimated_recovered_value = (
            offcut_intelligence_report.estimated_recovered_value
            if offcut_intelligence_report
            else 0.0
        )

        return WasteIntelligenceReport(
            waste_ratio=waste_ratio,
            waste_cost=cost_estimate.waste_cost,
            recovery_score=recovery_score,
            risk_level=risk_level,
            recommendation=recommendation,
            warnings=warnings,
            reuse_rate=reuse_rate,
            reusable_area=reusable_area,
            largest_reusable_area=largest_reusable_area,
            estimated_recovered_value=estimated_recovered_value,
        )
