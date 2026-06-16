from cost_intelligence.manufacturing_executive_report import (
    ManufacturingExecutiveReport,
)


class ManufacturingExecutiveReportBuilder:

    def build(
        self,
        manufacturing_kpi_report,
        production_readiness_report,
        manufacturing_optimization_result,
        *,
        capacity_report=None,
        production_schedule_report=None,
        factory_workload_report=None,
        manufacturing_complexity_report=None,
    ):
        recovery_score = (
            manufacturing_optimization_result.nesting_intelligence_report
            .recovery_score
        )
        capacity_status = (
            capacity_report.capacity_status if capacity_report else "AVAILABLE"
        )
        schedule_risk_level = (
            production_schedule_report.schedule_risk_level
            if production_schedule_report
            else "LOW"
        )
        workload_status = (
            factory_workload_report.factory_workload_status
            if factory_workload_report
            else "AVAILABLE"
        )
        complexity_level = (
            manufacturing_complexity_report.complexity_level
            if manufacturing_complexity_report
            else "LOW"
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
        if capacity_status == "LIMITED":
            score -= 5
        elif capacity_status == "OVERLOADED":
            score -= 15
        if schedule_risk_level == "MEDIUM":
            score -= 5
        elif schedule_risk_level == "HIGH":
            score -= 15
        if workload_status == "BUSY":
            score -= 5
        elif workload_status == "OVERLOADED":
            score -= 15
        if complexity_level == "MEDIUM":
            score -= 5
        elif complexity_level == "HIGH":
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
        if capacity_report:
            warnings.extend(capacity_report.warnings)
        if production_schedule_report:
            warnings.extend(production_schedule_report.warnings)
        if factory_workload_report:
            warnings.extend(factory_workload_report.warnings)
        if manufacturing_complexity_report:
            warnings.extend(manufacturing_complexity_report.warnings)

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
            recommendations=(
                list(production_readiness_report.recommendations)
                + (
                    list(manufacturing_complexity_report.recommendations)
                    if manufacturing_complexity_report
                    else []
                )
            ),
        )
