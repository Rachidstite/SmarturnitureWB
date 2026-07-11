from __future__ import annotations

from dataclasses import dataclass, field

from domain.anchors import AnchorCoordinate, EdgeRef, HardwarePlacement, MountFace
from domain.base_cabinet_engineering_entry import (
    build_base_cabinet_engineering_cabinet,
)
from domain.builders import CabinetProject
from domain.hardware_library import HardwareRegistry
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.rules_engine import RuleContext, build_rule_context_from_params
from domain.system32 import System32Engine
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from manufacturing.manufacturing_cutlist_builder import ManufacturingCutlistBuilder
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)
from shared.identity import PanelIdentity, normalize_identity_part


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

    _inject_base_cabinet_hinge_hardware(cabinet, scene_graph)
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


def _inject_base_cabinet_hinge_hardware(cabinet, scene_graph):
    construction_model = getattr(cabinet, "construction_model", None)
    engineering_model = getattr(cabinet, "engineering_model", None)
    construction_doors = list(getattr(construction_model, "doors", ()) or ())
    engineering_doors = list(getattr(engineering_model, "doors", ()) or ())
    if not construction_doors or not engineering_doors:
        return

    cabinet_id = _resolve_cabinet_id(cabinet)
    placements = []
    for construction_door, engineering_door in zip(
        construction_doors,
        engineering_doors,
    ):
        door_node_id = PanelIdentity.make_door(
            cabinet_id,
            engineering_door.section_index,
            engineering_door.door_index,
        ).key
        if scene_graph.get_node(door_node_id) is None:
            continue

        hinge_positions = tuple(
            System32Engine.hinge_positions(construction_door.height_mm)
        )[: int(getattr(construction_door, "hinge_count", 0) or 0)]
        hinge_side = _resolve_hinge_side(
            construction_door,
            engineering_door,
        )
        host_node_id = PanelIdentity.make_side(cabinet_id, hinge_side).key
        if scene_graph.get_node(host_node_id) is None:
            continue
        for ordinal, position in enumerate(hinge_positions, start=1):
            placement = HardwarePlacement(
                host_node_id=host_node_id,
                target_node_id=door_node_id,
                hardware_intent="INTENT_HINGE",
                anchor=AnchorCoordinate(
                    face=MountFace.BACK,
                    edge=EdgeRef.BOTTOM,
                    offset_x=22.0,
                    offset_y=position,
                ),
                description=f"Hinge {ordinal}/{len(hinge_positions)}",
            )
            placement.component_reference = door_node_id
            placement.cabinet_reference = cabinet_id
            placement.source_operation_reference = (
                f"{door_node_id}::hinge-{ordinal}"
            )
            placement.hinge_family = getattr(
                construction_door,
                "hardware_family",
                "",
            )
            placement.hinge_side = str(hinge_side or "")
            placement.hinge_ordinal = ordinal
            placement.resolved_hinge_count = len(hinge_positions)
            placements.append(placement)

    if not placements:
        return

    project = CabinetProject(
        graph=scene_graph,
        joinery=getattr(cabinet, "assembly_graph", None),
        topology=None,
        placements=placements,
    )
    rule_context = build_rule_context_from_params(cabinet.params)
    registry = HardwareRegistry()
    hinge_sku = str(
        rule_context.hardware_profile.get("INTENT_HINGE", "") or ""
    ).strip()
    if not hinge_sku or registry.get_hardware(hinge_sku) is None:
        rule_context.hardware_profile["INTENT_HINGE"] = RuleContext().hardware_profile[
            "INTENT_HINGE"
        ]
    ManufacturingCompiler().compile(
        project,
        rule_context,
    )


def _resolve_cabinet_id(cabinet) -> str:
    params = getattr(cabinet, "params", None)
    width = int(round(float(getattr(params, "width", 0.0) or 0.0)))
    height = int(round(float(getattr(params, "height", 0.0) or 0.0)))
    depth = int(round(float(getattr(params, "depth", 0.0) or 0.0)))
    sec_count = int(getattr(params, "sec_count", 1) or 1)
    return normalize_identity_part(f"CAB-{width}x{height}x{depth}-S{sec_count}")


def _resolve_hinge_side(construction_door, engineering_door) -> str:
    construction_hinge_side = getattr(
        getattr(construction_door, "hinge_side", None),
        "value",
        getattr(construction_door, "hinge_side", ""),
    )
    engineering_hinge_side = getattr(engineering_door, "hinge_side", "")
    return str(construction_hinge_side or engineering_hinge_side or "").strip().upper()
