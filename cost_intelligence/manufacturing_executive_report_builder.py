from cost_intelligence.manufacturing_executive_report import (
    ManufacturingExecutiveReport,
)


class ManufacturingExecutiveReportBuilder:

    def build(
        self,
        manufacturing_kpi_report,
        production_readiness_report,
        manufacturing_optimization_result,
    ):
        recovery_score = (
            manufacturing_optimization_result.nesting_intelligence_report
            .recovery_score
        )
        score = 100

        if manufacturing_kpi_report.production_status == "BLOCKED":
            score -= 40
        elif manufacturing_kpi_report.production_status == "READY_WITH_WARNINGS":
            score -= 15
        if manufacturing_kpi_report.gross_margin_rate <= 0:
            score -= 20
        if manufacturing_kpi_report.gross_margin_rate < 0.15:
            score -= 10
        if manufacturing_kpi_report.utilization_rate < 0.60:
            score -= 15
        if manufacturing_kpi_report.waste_rate > 0.30:
            score -= 10
        if recovery_score < 40:
            score -= 10

        score = max(0, min(100, score))

        if score >= 85:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 55:
            grade = "C"
        elif score >= 40:
            grade = "D"
        else:
            grade = "F"

        warnings = list(manufacturing_kpi_report.warnings)
        warnings.extend(production_readiness_report.warnings)

        return ManufacturingExecutiveReport(
            overall_score=score,
            overall_grade=grade,
            production_status=manufacturing_kpi_report.production_status,
            total_manufacturing_cost=(
                manufacturing_kpi_report.total_manufacturing_cost
            ),
            gross_margin_rate=manufacturing_kpi_report.gross_margin_rate,
            utilization_rate=manufacturing_kpi_report.utilization_rate,
            waste_rate=manufacturing_kpi_report.waste_rate,
            recovery_score=recovery_score,
            warnings=warnings,
            recommendations=list(production_readiness_report.recommendations),
        )
