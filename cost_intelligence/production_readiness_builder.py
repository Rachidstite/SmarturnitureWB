from cost_intelligence.production_readiness_report import (
    ProductionReadinessReport,
)


class ProductionReadinessBuilder:

    def build(
        self,
        manufacturing_production_package,
        manufacturing_cost_summary,
        manufacturing_optimization_result,
        manufacturing_commercial_result,
    ):
        nesting_report = (
            manufacturing_optimization_result.nesting_intelligence_report
        )
        profitability_report = (
            manufacturing_commercial_result.profitability_report
        )
        manufacturing_ready = manufacturing_production_package.release_ready
        profitability_ok = profitability_report.gross_profit > 0

        blocking_issues = []
        if not manufacturing_ready:
            blocking_issues.append(
                "Manufacturing production package is not release ready"
            )
        if manufacturing_cost_summary.risk_level == "HIGH":
            blocking_issues.append("Manufacturing cost risk is HIGH")
        if not profitability_ok:
            blocking_issues.append("Profitability is not positive")

        warnings = list(manufacturing_production_package.warnings)
        warnings.extend(manufacturing_cost_summary.warnings)
        warnings.extend(nesting_report.warnings)
        warnings.extend(profitability_report.warnings)

        if blocking_issues:
            status = "BLOCKED"
        elif warnings or nesting_report.risk_level == "MEDIUM":
            status = "READY_WITH_WARNINGS"
        else:
            status = "READY"

        recommendations = []
        risk_report = manufacturing_cost_summary.risk_report
        if risk_report and risk_report.recommendation:
            recommendations.append(risk_report.recommendation)
        if nesting_report.recommendation:
            recommendations.append(nesting_report.recommendation)

        return ProductionReadinessReport(
            status=status,
            manufacturing_ready=manufacturing_ready,
            cost_risk_level=manufacturing_cost_summary.risk_level,
            nesting_risk_level=nesting_report.risk_level,
            profitability_ok=profitability_ok,
            blocking_issues=blocking_issues,
            warnings=warnings,
            recommendations=recommendations,
        )
