from cost_intelligence.consumption_report import ConsumptionReport
from cost_intelligence.cost_estimate import CostEstimate
from cost_intelligence.scene_graph_cost_service import SceneGraphCostService
from cost_intelligence.manufacturing_factory_intelligence_pipeline_builder import (
    ManufacturingFactoryIntelligencePipelineBuilder,
)
from manufacturing.manufacturing_project_intelligence_result import (
    ManufacturingProjectIntelligenceResult,
)
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)
from cost_intelligence.sheet_utilization_builder import SheetUtilizationBuilder
from exports.cutlist_engine import CutListEngine
from exports.nesting_engine import IndustrialNestingEngine
from exports.strategies import GuillotineStripStrategy


class ManufacturingProjectIntelligencePipelineBuilder:

    def build(self, scene_graph, markup_rate=0.0, currency="MAD"):
        manufacturing_runtime_result = ManufacturingRuntimePipelineBuilder().build(
            scene_graph
        )
        cutlist_items = CutListEngine.extract(scene_graph)
        sheet_results = IndustrialNestingEngine(
            GuillotineStripStrategy()
        ).process(cutlist_items)
        sheet_utilization_report = SheetUtilizationBuilder().build(sheet_results)
        cost_report = SceneGraphCostService.estimate(scene_graph)
        consumption_report = ConsumptionReport(
            waste_ratio=sheet_utilization_report.waste_rate,
            warnings=list(cost_report.warnings) + list(sheet_utilization_report.warnings),
        )
        cost_estimate = CostEstimate(
            waste_cost=cost_report.waste_cost,
            warnings=list(cost_report.warnings) + list(sheet_utilization_report.warnings),
        )
        manufacturing_factory_intelligence_result = (
            ManufacturingFactoryIntelligencePipelineBuilder().build(
                manufacturing_runtime_result.manufacturing_production_package,
                markup_rate,
                currency,
                sheet_results=sheet_results,
                consumption_report=consumption_report,
                cost_estimate=cost_estimate,
            )
        )
        return ManufacturingProjectIntelligenceResult(
            manufacturing_runtime_result=manufacturing_runtime_result,
            manufacturing_factory_intelligence_result=(
                manufacturing_factory_intelligence_result
            ),
        )
