from cost_intelligence.furniture_project_executive_report import (
    FurnitureProjectExecutiveReport,
)


class FurnitureProjectExecutiveReportBuilder:

    def build(
        self,
        furniture_project_summary,
        manufacturing_executive_report,
        factory_decision_report,
    ):
        warnings = list(manufacturing_executive_report.warnings)
        warnings.extend(factory_decision_report.warnings)

        recommendations = list(manufacturing_executive_report.recommendations)
        recommendations.extend(factory_decision_report.recommendations)

        return FurnitureProjectExecutiveReport(
            total_cabinets=furniture_project_summary.total_cabinets,
            total_physical_parts=(
                furniture_project_summary.total_physical_parts
            ),
            total_machining_operations=(
                furniture_project_summary.total_machining_operations
            ),
            overall_score=manufacturing_executive_report.overall_score,
            overall_grade=manufacturing_executive_report.overall_grade,
            decision_status=factory_decision_report.decision_status,
            production_status=manufacturing_executive_report.production_status,
            total_manufacturing_cost=(
                manufacturing_executive_report.total_manufacturing_cost
            ),
            gross_margin_rate=manufacturing_executive_report.gross_margin_rate,
            utilization_rate=manufacturing_executive_report.utilization_rate,
            waste_rate=manufacturing_executive_report.waste_rate,
            recovery_score=manufacturing_executive_report.recovery_score,
            warnings=warnings,
            recommendations=recommendations,
            project_profitability_status=(
                manufacturing_executive_report.project_profitability_status
            ),
            material_efficiency_status=(
                manufacturing_executive_report.material_efficiency_status
            ),
            waste_risk_status=manufacturing_executive_report.waste_risk_status,
            bottleneck_status=manufacturing_executive_report.bottleneck_status,
            production_readiness_status=(
                manufacturing_executive_report.production_readiness_status
            ),
            overall_management_status=(
                manufacturing_executive_report.overall_management_status
            ),
        )
