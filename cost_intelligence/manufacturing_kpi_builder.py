from cost_intelligence.manufacturing_kpi_report import ManufacturingKPIReport


class ManufacturingKPIBuilder:

    def build(
        self,
        manufacturing_cost_summary,
        manufacturing_optimization_result,
        manufacturing_commercial_result,
        production_readiness_report,
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

        return ManufacturingKPIReport(
            total_manufacturing_cost=(
                manufacturing_cost_summary.total_manufacturing_cost
            ),
            gross_margin_rate=(
                manufacturing_commercial_result.profitability_report
                .gross_margin_rate
            ),
            utilization_rate=sheet_utilization_report.utilization_rate,
            waste_rate=sheet_utilization_report.waste_rate,
            reuse_rate=offcut_intelligence_report.reuse_rate,
            production_status=production_readiness_report.status,
            warnings=warnings,
        )
