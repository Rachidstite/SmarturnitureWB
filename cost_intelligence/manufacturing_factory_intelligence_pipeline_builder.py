from cost_intelligence.manufacturing_commercial_pipeline_builder import (
    ManufacturingCommercialPipelineBuilder,
)
from cost_intelligence.manufacturing_cost_pipeline_builder import (
    ManufacturingCostPipelineBuilder,
)
from cost_intelligence.manufacturing_executive_report_builder import (
    ManufacturingExecutiveReportBuilder,
)
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


class ManufacturingFactoryIntelligencePipelineBuilder:

    def build(
        self,
        manufacturing_production_package,
        markup_rate=0.0,
        currency="MAD",
    ):
        manufacturing_cost_summary = ManufacturingCostPipelineBuilder().build(
            manufacturing_production_package
        )
        manufacturing_optimization_result = (
            ManufacturingOptimizationPipelineBuilder().build(
                manufacturing_production_package
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
        manufacturing_executive_report = (
            ManufacturingExecutiveReportBuilder().build(
                manufacturing_kpi_report,
                production_readiness_report,
                manufacturing_optimization_result,
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
