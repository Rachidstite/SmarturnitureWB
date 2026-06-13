from manufacturing.extractor import ManufacturingExtractor
from manufacturing.manufacturing_package_builder import ManufacturingPackageBuilder
from manufacturing.manufacturing_production_package_builder import (
    ManufacturingProductionPackageBuilder,
)
from manufacturing.manufacturing_runtime_result import ManufacturingRuntimeResult
from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class ManufacturingRuntimePipelineBuilder:

    def build(self, scene_graph):
        panel_specs = ManufacturingExtractor.extract(scene_graph)
        machining_operations = [
            operation
            for panel in panel_specs
            for operation in panel.cnc_operations
        ]
        edge_operations = [
            UnifiedManufacturingOperation(operation_type="EDGE_BANDING")
            for panel in panel_specs
            for _edge in panel.edge_spec.all_banded()
        ]
        manufacturing_package = ManufacturingPackageBuilder().build(
            panels=panel_specs,
            materials=[],
            machining_operations=machining_operations,
            edge_operations=edge_operations,
            warnings=[],
        )
        manufacturing_production_package = (
            ManufacturingProductionPackageBuilder().build(
                manufacturing_package
            )
        )
        return ManufacturingRuntimeResult(
            panel_specs=panel_specs,
            manufacturing_package=manufacturing_package,
            manufacturing_production_package=manufacturing_production_package,
        )
