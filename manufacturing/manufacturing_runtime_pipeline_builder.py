from manufacturing.extractor import ManufacturingExtractor
from manufacturing.manufacturing_package_builder import ManufacturingPackageBuilder
from manufacturing.manufacturing_operation_adapter import (
    ManufacturingOperationAdapter,
)
from manufacturing.manufacturing_production_package_builder import (
    ManufacturingProductionPackageBuilder,
)
from manufacturing.manufacturing_runtime_result import ManufacturingRuntimeResult
from manufacturing.material_spec import MATERIAL_LIBRARY
from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class ManufacturingRuntimePipelineBuilder:

    def build(self, scene_graph):
        panel_specs = ManufacturingExtractor.extract(scene_graph)
        materials = self._resolve_materials(panel_specs)
        machining_operations = ManufacturingOperationAdapter.to_unified_panel_operations(
            panel_specs
        )
        edge_operations = [
            UnifiedManufacturingOperation(operation_type="EDGE_BANDING")
            for panel in panel_specs
            for _edge in panel.edge_spec.all_banded()
        ]
        manufacturing_package = ManufacturingPackageBuilder().build(
            panels=panel_specs,
            materials=materials,
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

    @staticmethod
    def _resolve_materials(panel_specs):
        resolved = {}
        for panel in panel_specs or []:
            material_key = ManufacturingRuntimePipelineBuilder._normalize_material_key(
                getattr(panel, "material", "")
            )
            if not material_key:
                continue
            material_spec = MATERIAL_LIBRARY.get(material_key)
            if material_spec is None:
                continue
            resolved.setdefault(material_key, material_spec)
        return list(resolved.values())

    @staticmethod
    def _normalize_material_key(material_name):
        raw = str(material_name or "").strip()
        if not raw:
            return ""

        candidates = (
            raw,
            raw.upper(),
            f"{raw}MM",
            f"{raw.upper()}MM",
        )
        alias_map = {
            "MDF_18": "MDF_18MM",
            "HDF_3": "HDF_3MM",
            "MELAMINE_WHITE_18": "MELAMINE_WHITE_18MM",
        }
        for candidate in candidates:
            if candidate in MATERIAL_LIBRARY:
                return candidate
            alias = alias_map.get(candidate)
            if alias and alias in MATERIAL_LIBRARY:
                return alias
        return ""
