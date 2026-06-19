from cost_intelligence.manufacturing_cost_summary import ManufacturingCostSummary


class ManufacturingCostSummaryBuilder:

    def build(self, cost_report, risk_report, insights):
        return ManufacturingCostSummary(
            cost_report=cost_report,
            risk_report=risk_report,
            insights=insights,
            total_manufacturing_cost=cost_report.total_manufacturing_cost,
            hardware_cost=cost_report.hardware_cost,
            risk_level=risk_report.risk_level,
            warnings=risk_report.warnings,
        )
