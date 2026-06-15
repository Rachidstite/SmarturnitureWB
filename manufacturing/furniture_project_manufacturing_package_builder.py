from manufacturing.manufacturing_package_builder import ManufacturingPackageBuilder
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)


class FurnitureProjectManufacturingPackageBuilder:

    def build(self, furniture_project):
        panels = []
        materials = []
        machining_operations = []
        edge_operations = []
        warnings = []

        runtime_builder = ManufacturingRuntimePipelineBuilder()
        for cabinet in furniture_project.cabinets:
            runtime_result = runtime_builder.build(cabinet.graph)
            package = runtime_result.manufacturing_package
            panels.extend(package.panels)
            materials.extend(package.materials)
            machining_operations.extend(package.machining_operations)
            edge_operations.extend(package.edge_operations)
            warnings.extend(package.warnings)

        return ManufacturingPackageBuilder().build(
            panels=panels,
            materials=materials,
            machining_operations=machining_operations,
            edge_operations=edge_operations,
            warnings=warnings,
        )
