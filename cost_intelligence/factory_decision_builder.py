from cost_intelligence.factory_decision_report import FactoryDecisionReport


class FactoryDecisionBuilder:

    def build(
        self,
        production_readiness_report,
        manufacturing_cost_summary,
        waste_intelligence_report,
        nesting_intelligence_report,
        quotation_intelligence_report,
        *,
        capacity_report=None,
        production_schedule_report=None,
        factory_workload_report=None,
        manufacturing_complexity_report=None,
    ):
        risk_levels = (
            manufacturing_cost_summary.risk_level,
            waste_intelligence_report.risk_level,
            nesting_intelligence_report.risk_level,
            quotation_intelligence_report.risk_level,
        )
        capacity_status = (
            capacity_report.capacity_status
            if capacity_report
            else "AVAILABLE"
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

        if production_readiness_report.status == "BLOCKED":
            decision_status = "BLOCKED"
        elif "HIGH" in risk_levels:
            decision_status = "REVIEW_REQUIRED"
        elif production_readiness_report.status == "READY_WITH_WARNINGS":
            decision_status = "REVIEW_REQUIRED"
        elif capacity_status == "OVERLOADED":
            decision_status = "REVIEW_REQUIRED"
        elif schedule_risk_level == "HIGH":
            decision_status = "REVIEW_REQUIRED"
        elif workload_status == "OVERLOADED":
            decision_status = "REVIEW_REQUIRED"
        elif complexity_level == "HIGH":
            decision_status = "REVIEW_REQUIRED"
        else:
            decision_status = "APPROVED"

        warnings = list(production_readiness_report.warnings)
        warnings.extend(manufacturing_cost_summary.warnings)
        warnings.extend(waste_intelligence_report.warnings)
        warnings.extend(nesting_intelligence_report.warnings)
        if capacity_report:
            warnings.extend(capacity_report.warnings)
        if production_schedule_report:
            warnings.extend(production_schedule_report.warnings)
        if factory_workload_report:
            warnings.extend(factory_workload_report.warnings)
        if manufacturing_complexity_report:
            warnings.extend(manufacturing_complexity_report.warnings)

        recommendations = list(production_readiness_report.recommendations)
        if waste_intelligence_report.recommendation:
            recommendations.append(waste_intelligence_report.recommendation)
        if nesting_intelligence_report.recommendation:
            recommendations.append(nesting_intelligence_report.recommendation)
        recommendations.extend(quotation_intelligence_report.recommendations)
        if manufacturing_complexity_report:
            recommendations.extend(
                manufacturing_complexity_report.recommendations
            )

        return FactoryDecisionReport(
            decision_status=decision_status,
            manufacturing_ready=production_readiness_report.manufacturing_ready,
            profitability_ok=production_readiness_report.profitability_ok,
            cost_risk_level=manufacturing_cost_summary.risk_level,
            waste_risk_level=waste_intelligence_report.risk_level,
            nesting_risk_level=nesting_intelligence_report.risk_level,
            quotation_risk_level=quotation_intelligence_report.risk_level,
            margin_status=quotation_intelligence_report.margin_status,
            capacity_status=capacity_status,
            schedule_risk_level=schedule_risk_level,
            workload_status=workload_status,
            complexity_level=complexity_level,
            blocking_issues=list(production_readiness_report.blocking_issues),
            warnings=warnings,
            recommendations=recommendations,
        )
