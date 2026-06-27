from __future__ import annotations

from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_adapter import BaseCabinetSpecificationAdapter
from engine.cabinet import Cabinet

try:
    from engine.cabinet_builder import CabinetBuilder
except Exception:  # pragma: no cover - fallback for contract-only environments
    CabinetBuilder = None


def build_base_cabinet_engineering_cabinet(
    specification: BaseCabinetSpecification,
) -> Cabinet:
    adapter_result = BaseCabinetSpecificationAdapter.adapt(specification)
    cabinet = Cabinet(params=adapter_result.cabinet_params)

    if CabinetBuilder is None:
        raise RuntimeError("CabinetBuilder is unavailable")

    builder = CabinetBuilder()
    builder.build(cabinet)
    scene_graph = getattr(builder, "scene_graph", None)
    if scene_graph is not None:
        cabinet.graph = scene_graph
        cabinet.scene_graph = scene_graph
    return cabinet
