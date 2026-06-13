from cost_intelligence.manufacturing_cost_risk_report import (
    ManufacturingCostRiskReport,
)


class ManufacturingCostRiskReportBuilder:

    def build(self, insights):
        recommendations = {
            "LOW": "No manufacturing cost risks detected.",
            "MEDIUM": "Review manufacturing complexity before quotation.",
            "HIGH": (
                "Review manufacturing complexity before production release."
            ),
        }

        return ManufacturingCostRiskReport(
            risk_level=insights.risk_level,
            findings=insights.insights,
            recommendation=recommendations[insights.risk_level],
            warnings=insights.warnings,
        )
