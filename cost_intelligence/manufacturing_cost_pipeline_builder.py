from cost_intelligence.manufacturing_cost_calculator import (
    ManufacturingCostCalculator,
)
from cost_intelligence.manufacturing_cost_context_builder import (
    ManufacturingCostContextBuilder,
)
from cost_intelligence.manufacturing_cost_insights_builder import (
    ManufacturingCostInsightsBuilder,
)
from cost_intelligence.manufacturing_cost_risk_report_builder import (
    ManufacturingCostRiskReportBuilder,
)
from cost_intelligence.manufacturing_cost_summary_builder import (
    ManufacturingCostSummaryBuilder,
)
from manufacturing.manufacturing_metrics_builder import ManufacturingMetricsBuilder


class ManufacturingCostPipelineBuilder:

    def build(self, production_package):
        metrics_report = ManufacturingMetricsBuilder().build(production_package)
        context = ManufacturingCostContextBuilder().build(metrics_report)
        insights = ManufacturingCostInsightsBuilder().build(context)
        risk_report = ManufacturingCostRiskReportBuilder().build(insights)
        cost_report = ManufacturingCostCalculator().calculate(context)
        return ManufacturingCostSummaryBuilder().build(
            cost_report, risk_report, insights
        )
