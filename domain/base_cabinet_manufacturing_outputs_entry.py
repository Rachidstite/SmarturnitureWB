from __future__ import annotations

from dataclasses import dataclass, field

from domain.base_cabinet_engineering_entry import (
    build_base_cabinet_engineering_cabinet,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from manufacturing.manufacturing_cutlist_builder import ManufacturingCutlistBuilder
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)


@dataclass(frozen=True)
class BaseCabinetManufacturingOutputsEntryResult:
    cut_list: object
    manufacturing_package: object
    metadata: dict = field(default_factory=dict)


def build_base_cabinet_manufacturing_outputs_entry(
    specification: BaseCabinetSpecification,
) -> BaseCabinetManufacturingOutputsEntryResult:
    cabinet = build_base_cabinet_engineering_cabinet(specification)
    scene_graph = getattr(cabinet, "graph", None) or getattr(
        cabinet,
        "scene_graph",
        None,
    )
    if scene_graph is None:
        raise RuntimeError("Engineering cabinet did not expose a scene graph")

    runtime_result = ManufacturingRuntimePipelineBuilder().build(scene_graph)
    cut_list = ManufacturingCutlistBuilder().build(
        runtime_result.manufacturing_package
    )
    adapter_result = BaseCabinetSpecificationAdapter.adapt(specification)

    return BaseCabinetManufacturingOutputsEntryResult(
        cut_list=cut_list,
        manufacturing_package=runtime_result.manufacturing_package,
        metadata=dict(adapter_result.metadata),
    )
