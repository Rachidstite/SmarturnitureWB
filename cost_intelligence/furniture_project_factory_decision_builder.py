from cost_intelligence.factory_decision_builder import FactoryDecisionBuilder
from cost_intelligence.manufacturing_factory_intelligence_pipeline_builder import (
    ManufacturingFactoryIntelligencePipelineBuilder,
)
from manufacturing.furniture_project_manufacturing_package_builder import (
    FurnitureProjectManufacturingPackageBuilder,
)
from manufacturing.manufacturing_production_package_builder import (
    ManufacturingProductionPackageBuilder,
)


class FurnitureProjectFactoryDecisionBuilder:

    def build(
        self,
        furniture_project,
        markup_rate=0.0,
        currency="MAD",
    ):
        manufacturing_package = (
            FurnitureProjectManufacturingPackageBuilder().build(
                furniture_project
            )
        )
        manufacturing_production_package = (
            ManufacturingProductionPackageBuilder().build(
                manufacturing_package
            )
        )
        factory_result = ManufacturingFactoryIntelligencePipelineBuilder().build(
            manufacturing_production_package,
            markup_rate,
            currency,
        )

        return FactoryDecisionBuilder().build(
            factory_result.production_readiness_report,
            factory_result.manufacturing_cost_summary,
            (
                factory_result.manufacturing_optimization_result
                .waste_intelligence_report
            ),
            (
                factory_result.manufacturing_optimization_result
                .nesting_intelligence_report
            ),
            (
                factory_result.manufacturing_commercial_result
                .quotation_intelligence_report
            ),
        )
