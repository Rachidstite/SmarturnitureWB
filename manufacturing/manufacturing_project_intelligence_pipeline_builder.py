from cost_intelligence.manufacturing_factory_intelligence_pipeline_builder import (
    ManufacturingFactoryIntelligencePipelineBuilder,
)
from manufacturing.manufacturing_project_intelligence_result import (
    ManufacturingProjectIntelligenceResult,
)
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)


class ManufacturingProjectIntelligencePipelineBuilder:

    def build(self, scene_graph, markup_rate=0.0, currency="MAD"):
        manufacturing_runtime_result = ManufacturingRuntimePipelineBuilder().build(
            scene_graph
        )
        manufacturing_factory_intelligence_result = (
            ManufacturingFactoryIntelligencePipelineBuilder().build(
                manufacturing_runtime_result.manufacturing_production_package,
                markup_rate,
                currency,
            )
        )
        return ManufacturingProjectIntelligenceResult(
            manufacturing_runtime_result=manufacturing_runtime_result,
            manufacturing_factory_intelligence_result=(
                manufacturing_factory_intelligence_result
            ),
        )
