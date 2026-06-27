from __future__ import annotations

from domain.base_cabinet_engineering_entry import (
    build_base_cabinet_engineering_cabinet,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from manufacturing.manufacturing_cutlist_builder import ManufacturingCutlistBuilder
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)


def build_base_cabinet_cutlist(
    specification: BaseCabinetSpecification,
):
    cabinet = build_base_cabinet_engineering_cabinet(specification)
    scene_graph = getattr(cabinet, "graph", None) or getattr(
        cabinet,
        "scene_graph",
        None,
    )
    if scene_graph is None:
        raise RuntimeError("Engineering cabinet did not expose a scene graph")

    runtime_result = ManufacturingRuntimePipelineBuilder().build(scene_graph)
    return ManufacturingCutlistBuilder().build(runtime_result.manufacturing_package)
