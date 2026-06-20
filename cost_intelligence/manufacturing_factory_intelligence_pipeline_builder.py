from cost_intelligence.manufacturing_commercial_pipeline_builder import (
    ManufacturingCommercialPipelineBuilder,
)
from cost_intelligence.manufacturing_cost_pipeline_builder import (
    ManufacturingCostPipelineBuilder,
)
from cost_intelligence.manufacturing_executive_report_builder import (
    ManufacturingExecutiveReportBuilder,
)
from cost_intelligence.consumption_report import ConsumptionReport
from cost_intelligence.cost_estimate import CostEstimate
from cost_intelligence.manufacturing_factory_intelligence_result import (
    ManufacturingFactoryIntelligenceResult,
)
from cost_intelligence.manufacturing_kpi_builder import ManufacturingKPIBuilder
from cost_intelligence.manufacturing_optimization_pipeline_builder import (
    ManufacturingOptimizationPipelineBuilder,
)
from cost_intelligence.production_readiness_builder import (
    ProductionReadinessBuilder,
)
from manufacturing.factory_workload_builder import FactoryWorkloadBuilder
from manufacturing.manufacturing_capacity_builder import (
    ManufacturingCapacityBuilder,
)
from manufacturing.manufacturing_complexity_builder import (
    ManufacturingComplexityBuilder,
)
from manufacturing.manufacturing_duration_builder import (
    ManufacturingDurationBuilder,
)
from manufacturing.manufacturing_metrics_builder import (
    ManufacturingMetricsBuilder,
)
from manufacturing.production_schedule_builder import ProductionScheduleBuilder


class ManufacturingFactoryIntelligencePipelineBuilder:

    def build(
        self,
        manufacturing_production_package,
        markup_rate=0.0,
        currency="MAD",
        sheet_results=None,
        consumption_report=None,
        cost_estimate=None,
    ):
        sheet_results = sheet_results or []
        consumption_report = consumption_report or ConsumptionReport()
        cost_estimate = cost_estimate or CostEstimate()
        manufacturing_cost_summary = ManufacturingCostPipelineBuilder().build(
            manufacturing_production_package
        )
        manufacturing_optimization_result = (
            ManufacturingOptimizationPipelineBuilder().build(
                sheet_results,
                consumption_report,
                cost_estimate,
            )
        )
        manufacturing_commercial_result = (
            ManufacturingCommercialPipelineBuilder().build(
                manufacturing_production_package,
                markup_rate,
                currency,
            )
        )
        production_readiness_report = ProductionReadinessBuilder().build(
            manufacturing_production_package,
            manufacturing_cost_summary,
            manufacturing_optimization_result,
            manufacturing_commercial_result,
        )
        manufacturing_kpi_report = ManufacturingKPIBuilder().build(
            manufacturing_cost_summary,
            manufacturing_optimization_result,
            manufacturing_commercial_result,
            production_readiness_report,
        )
        manufacturing_metrics_report = ManufacturingMetricsBuilder().build(
            manufacturing_production_package
        )
        manufacturing_duration_report = ManufacturingDurationBuilder().build(
            manufacturing_metrics_report
        )
        manufacturing_capacity_report = ManufacturingCapacityBuilder().build(
            manufacturing_duration_report
        )
        production_schedule_report = ProductionScheduleBuilder().build(
            manufacturing_duration_report,
            manufacturing_capacity_report,
        )
        factory_workload_report = FactoryWorkloadBuilder().build(
            [production_schedule_report]
        )
        manufacturing_complexity_report = (
            ManufacturingComplexityBuilder().build(
                manufacturing_metrics_report
            )
        )
        manufacturing_executive_report = (
            ManufacturingExecutiveReportBuilder().build(
                manufacturing_kpi_report,
                production_readiness_report,
                manufacturing_optimization_result,
                capacity_report=manufacturing_capacity_report,
                production_schedule_report=production_schedule_report,
                factory_workload_report=factory_workload_report,
                manufacturing_complexity_report=(
                    manufacturing_complexity_report
                ),
            )
        )
        return ManufacturingFactoryIntelligenceResult(
            manufacturing_cost_summary=manufacturing_cost_summary,
            manufacturing_optimization_result=manufacturing_optimization_result,
            manufacturing_commercial_result=manufacturing_commercial_result,
            production_readiness_report=production_readiness_report,
            manufacturing_kpi_report=manufacturing_kpi_report,
            manufacturing_executive_report=manufacturing_executive_report,
        )
