from cost_intelligence.manufacturing_kpi_report import ManufacturingKPIReport


class ManufacturingKPIBuilder:

    def build(
        self,
        manufacturing_cost_summary,
        manufacturing_optimization_result,
        manufacturing_commercial_result,
        production_readiness_report,
        factory_bottleneck_intelligence_report=None,
    ):
        sheet_utilization_report = (
            manufacturing_optimization_result.sheet_utilization_report
        )
        offcut_intelligence_report = (
            manufacturing_optimization_result.offcut_intelligence_report
        )
        waste_intelligence_report = (
            manufacturing_optimization_result.waste_intelligence_report
        )
        nesting_intelligence_report = (
            manufacturing_optimization_result.nesting_intelligence_report
        )

        warnings = list(manufacturing_cost_summary.warnings)
        warnings.extend(sheet_utilization_report.warnings)
        warnings.extend(offcut_intelligence_report.warnings)
        warnings.extend(waste_intelligence_report.warnings)
        warnings.extend(nesting_intelligence_report.warnings)
        warnings.extend(production_readiness_report.warnings)

        gross_margin_rate = (
            manufacturing_commercial_result.profitability_report
            .gross_margin_rate
        )
        utilization_rate = sheet_utilization_report.utilization_rate
        waste_rate = sheet_utilization_report.waste_rate
        reuse_rate = offcut_intelligence_report.reuse_rate
        production_status = production_readiness_report.status
        bottleneck_status = getattr(
            factory_bottleneck_intelligence_report,
            "severity",
            "UNKNOWN",
        )

        return ManufacturingKPIReport(
            total_manufacturing_cost=(
                manufacturing_cost_summary.total_manufacturing_cost
            ),
            gross_margin_rate=gross_margin_rate,
            utilization_rate=utilization_rate,
            waste_rate=waste_rate,
            reuse_rate=reuse_rate,
            production_status=production_status,
            warnings=warnings,
            project_profitability_status=self._profitability_status(
                gross_margin_rate
            ),
            material_efficiency_status=self._material_efficiency_status(
                utilization_rate,
                reuse_rate,
            ),
            waste_risk_status=self._waste_risk_status(waste_rate),
            bottleneck_status=bottleneck_status,
            production_readiness_status=production_status,
            overall_management_status=self._overall_management_status(
                gross_margin_rate=gross_margin_rate,
                waste_rate=waste_rate,
                production_status=production_status,
                bottleneck_status=bottleneck_status,
            ),
        )

    @staticmethod
    def _profitability_status(gross_margin_rate):
        if gross_margin_rate <= 0.0:
            return "CRITICAL"
        if gross_margin_rate < 0.15:
            return "LOW"
        return "HEALTHY"

    @staticmethod
    def _material_efficiency_status(utilization_rate, reuse_rate):
        if utilization_rate >= 0.75 and reuse_rate >= 0.50:
            return "EFFICIENT"
        if utilization_rate < 0.60 or reuse_rate < 0.25:
            return "INEFFICIENT"
        return "STABLE"

    @staticmethod
    def _waste_risk_status(waste_rate):
        if waste_rate > 0.30:
            return "HIGH"
        if waste_rate > 0.20:
            return "MEDIUM"
        return "LOW"

    @classmethod
    def _overall_management_status(
        cls,
        *,
        gross_margin_rate,
        waste_rate,
        production_status,
        bottleneck_status,
    ):
        if (
            production_status == "BLOCKED"
            or cls._profitability_status(gross_margin_rate) == "CRITICAL"
            or cls._waste_risk_status(waste_rate) == "HIGH"
            or bottleneck_status == "HIGH"
        ):
            return "ACTION_REQUIRED"
        if (
            production_status != "READY"
            or cls._profitability_status(gross_margin_rate) == "LOW"
            or cls._waste_risk_status(waste_rate) == "MEDIUM"
            or bottleneck_status == "MEDIUM"
        ):
            return "MONITOR"
        return "HEALTHY"
