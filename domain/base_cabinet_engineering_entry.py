from __future__ import annotations

from dataclasses import replace

from domain.base_cabinet_engineering_model import EngineeringPanelPlacement
from domain.base_cabinet_engineering_model import BaseCabinetEngineeringModelBuilder
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_adapter import BaseCabinetSpecificationAdapter
from domain.construction_resolver import ConstructionResolver
from engine.cabinet import Cabinet

try:
    from engine.cabinet_builder import CabinetBuilder
except Exception:  # pragma: no cover - fallback for contract-only environments
    CabinetBuilder = None


_PLINTH_OFFSET_MM = 20.0


def build_base_cabinet_engineering_cabinet(
    specification: BaseCabinetSpecification,
) -> Cabinet:
    adapter_result = BaseCabinetSpecificationAdapter.adapt(specification)
    cabinet = Cabinet(params=adapter_result.cabinet_params)
    attach_base_cabinet_engineering_models(cabinet, specification)

    if CabinetBuilder is None:
        raise RuntimeError("CabinetBuilder is unavailable")

    builder = CabinetBuilder()
    builder.build(cabinet)
    scene_graph = getattr(builder, "scene_graph", None)
    if scene_graph is None:
        raise RuntimeError("Engineering cabinet build did not produce a scene graph")
    cabinet.graph = scene_graph
    cabinet.scene_graph = scene_graph
    return cabinet


def attach_base_cabinet_engineering_models(
    cabinet: Cabinet,
    specification: BaseCabinetSpecification,
) -> Cabinet:
    cabinet.construction_model = ConstructionResolver.resolve(specification)
    engineering_model = BaseCabinetEngineeringModelBuilder.build(
        cabinet.construction_model
    )
    base_height = float(getattr(cabinet.params, "base_height", 0.0) or 0.0)
    if specification.toe_kick_required and base_height > 0.0:
        thickness = engineering_model.left_side_panel.thickness_mm
        inner_width = engineering_model.bottom_panel.width_mm
        cabinet_depth = engineering_model.left_side_panel.depth_mm
        back_thickness = float(
            getattr(cabinet.params, "back_thickness", 0.0) or 0.0
        )
        plinth_panels = (
            EngineeringPanelPlacement(
                role="PLINTH",
                name="Plinth Front",
                width_mm=inner_width,
                depth_mm=thickness,
                height_mm=base_height,
                position_mm=(thickness, _PLINTH_OFFSET_MM, 0.0),
                thickness_mm=thickness,
                material=engineering_model.left_side_panel.material,
            ),
            EngineeringPanelPlacement(
                role="PLINTH",
                name="Plinth Back",
                width_mm=inner_width,
                depth_mm=thickness,
                height_mm=base_height,
                position_mm=(
                    thickness,
                    cabinet_depth - _PLINTH_OFFSET_MM - back_thickness - thickness,
                    0.0,
                ),
                thickness_mm=thickness,
                material=engineering_model.left_side_panel.material,
            ),
        )
        engineering_model = replace(
            engineering_model,
            plinth_panels=plinth_panels,
        )
    cabinet.engineering_model = engineering_model
    return cabinet
