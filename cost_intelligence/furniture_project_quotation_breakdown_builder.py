from cost_intelligence.manufacturing_commercial_pipeline_builder import (
    ManufacturingCommercialPipelineBuilder,
)
from manufacturing.manufacturing_production_package_builder import (
    ManufacturingProductionPackageBuilder,
)
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)


class FurnitureProjectQuotationBreakdownBuilder:

    def build(self, furniture_project, markup_rate=0.0, currency="MAD"):
        breakdowns = []

        runtime_builder = ManufacturingRuntimePipelineBuilder()
        production_package_builder = ManufacturingProductionPackageBuilder()
        commercial_pipeline_builder = ManufacturingCommercialPipelineBuilder()

        for index, cabinet in enumerate(furniture_project.cabinets, start=1):
            runtime_result = runtime_builder.build(cabinet.graph)
            manufacturing_production_package = (
                production_package_builder.build(
                    runtime_result.manufacturing_package
                )
            )
            commercial_result = commercial_pipeline_builder.build(
                manufacturing_production_package,
                markup_rate,
                currency,
            )

            breakdowns.append(
                {
                    "cabinet_index": index,
                    "total_manufacturing_cost": (
                        commercial_result
                        .manufacturing_cost_summary
                        .total_manufacturing_cost
                    ),
                    "selling_price": (
                        commercial_result
                        .quotation_report
                        .selling_price
                    ),
                    "currency": commercial_result.quotation_report.currency,
                    "risk_level": (
                        commercial_result
                        .manufacturing_cost_summary
                        .risk_level
                    ),
                }
            )

        return breakdowns
