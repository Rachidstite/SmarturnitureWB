from cost_intelligence.factory_decision_report import FactoryDecisionReport


class FactoryDecisionBuilder:

    def build(
        self,
        production_readiness_report,
        manufacturing_cost_summary,
        waste_intelligence_report,
        nesting_intelligence_report,
        quotation_intelligence_report,
        manufacturing_decision_reports=None,
    ):
        risk_levels = (
            manufacturing_cost_summary.risk_level,
            waste_intelligence_report.risk_level,
            nesting_intelligence_report.risk_level,
            quotation_intelligence_report.risk_level,
        )

        if production_readiness_report.status == "BLOCKED":
            decision_status = "BLOCKED"
        elif "HIGH" in risk_levels:
            decision_status = "REVIEW_REQUIRED"
        elif production_readiness_report.status == "READY_WITH_WARNINGS":
            decision_status = "REVIEW_REQUIRED"
        else:
            decision_status = "APPROVED"

        warnings = list(production_readiness_report.warnings)
        warnings.extend(manufacturing_cost_summary.warnings)
        warnings.extend(waste_intelligence_report.warnings)
        warnings.extend(nesting_intelligence_report.warnings)

        recommendations = list(production_readiness_report.recommendations)
        if waste_intelligence_report.recommendation:
            recommendations.append(waste_intelligence_report.recommendation)
        if nesting_intelligence_report.recommendation:
            recommendations.append(nesting_intelligence_report.recommendation)
        recommendations.extend(quotation_intelligence_report.recommendations)

        blocking_issues = list(production_readiness_report.blocking_issues)
        decision_status = self._apply_manufacturing_decision_signals(
            decision_status,
            warnings,
            recommendations,
            blocking_issues,
            manufacturing_decision_reports,
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
            blocking_issues=blocking_issues,
            warnings=warnings,
            recommendations=recommendations,
        )

    @staticmethod
    def _apply_manufacturing_decision_signals(
        decision_status,
        warnings,
        recommendations,
        blocking_issues,
        manufacturing_decision_reports,
    ):
        reports = list(manufacturing_decision_reports or [])

        has_blocked = False
        has_review = False

        for report in reports:
            if getattr(report, "blocking_reason", ""):
                blocking_issues.append(getattr(report, "blocking_reason"))
            if getattr(report, "warning_reason", ""):
                warnings.append(getattr(report, "warning_reason"))
            if getattr(report, "recommended_fix", ""):
                recommendations.append(getattr(report, "recommended_fix"))

            has_blocked = has_blocked or bool(getattr(report, "is_blocked", False))
            has_review = has_review or bool(
                getattr(report, "requires_review", False)
            )

        if has_blocked:
            return "BLOCKED"

        if has_review and decision_status != "BLOCKED":
            return "REVIEW_REQUIRED"

        return decision_status
