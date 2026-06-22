from cost_intelligence.nesting_intelligence_report import (
    NestingIntelligenceReport,
)


class NestingIntelligenceBuilder:

    @staticmethod
    def _get_instance_field(instance, field_name, default=None):
        instance_dict = getattr(instance, "__dict__", {})
        if field_name in instance_dict:
            return instance_dict[field_name]
        return default

    def build(
        self,
        sheet_utilization_report,
        offcut_intelligence_report,
        waste_intelligence_report,
    ):
        reuse_rate = self._get_instance_field(waste_intelligence_report, "reuse_rate")
        if reuse_rate is None:
            reuse_rate = self._get_instance_field(
                offcut_intelligence_report,
                "reuse_rate",
                0.0,
            )

        reusable_area = self._get_instance_field(
            waste_intelligence_report,
            "reusable_area",
        )
        if reusable_area is None:
            reusable_area = self._get_instance_field(
                offcut_intelligence_report,
                "reusable_area",
                0.0,
            )

        estimated_recovered_value = self._get_instance_field(
            waste_intelligence_report,
            "estimated_recovered_value",
        )
        if estimated_recovered_value is None:
            estimated_recovered_value = self._get_instance_field(
                offcut_intelligence_report,
                "estimated_recovered_value",
                0.0,
            )

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
            reuse_rate=reuse_rate,
            reusable_area=reusable_area,
            estimated_recovered_value=estimated_recovered_value,
        )
