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
from manufacturing.labor_cost_builder import LaborCostBuilder
from manufacturing.manufacturing_duration_builder import (
    ManufacturingDurationBuilder,
)
from manufacturing.manufacturing_metrics_builder import ManufacturingMetricsBuilder


class ManufacturingCostPipelineBuilder:

    def build(self, production_package, hardware_cost=0.0,
              cnc_hourly_rate=0.0, drilling_hourly_rate=0.0,
              edge_banding_hourly_rate=0.0, assembly_hourly_rate=0.0,
              sheet_cost=None, waste_cost=None, recovered_value=None):
        metrics_report = ManufacturingMetricsBuilder().build(production_package)
        context = ManufacturingCostContextBuilder().build(metrics_report)
        duration_report = ManufacturingDurationBuilder().build(metrics_report)
        labor_cost_report = LaborCostBuilder(
            cnc_hourly_rate=cnc_hourly_rate,
            drilling_hourly_rate=drilling_hourly_rate,
            edge_banding_hourly_rate=edge_banding_hourly_rate,
            assembly_hourly_rate=assembly_hourly_rate,
        ).build(duration_report)
        insights = ManufacturingCostInsightsBuilder().build(context)
        risk_report = ManufacturingCostRiskReportBuilder().build(insights)
        cost_report = ManufacturingCostCalculator().calculate(
            context,
            hardware_cost=hardware_cost,
            labor_cost_report=labor_cost_report,
            sheet_cost=sheet_cost,
            waste_cost=waste_cost,
            recovered_value=recovered_value,
        )
        return ManufacturingCostSummaryBuilder().build(
            cost_report, risk_report, insights
        )
