from __future__ import annotations

from dataclasses import replace

from domain.back_panel_engine import BackPanelRule
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


def _enrich_toe_kick_engineering_placement(
    engineering_model,
    *,
    base_height: float,
    toe_kick_required: bool,
    back_thickness: float,
):
    if not toe_kick_required or base_height <= 0.0:
        return engineering_model

    thickness = engineering_model.left_side_panel.thickness_mm
    cabinet_depth = engineering_model.left_side_panel.depth_mm
    cabinet_height = engineering_model.left_side_panel.height_mm
    bottom_panel = replace(
        engineering_model.bottom_panel,
        position_mm=(
            engineering_model.bottom_panel.position_mm[0],
            engineering_model.bottom_panel.position_mm[1],
            base_height,
        ),
    )

    back_panel = engineering_model.back_panel
    if back_panel is not None:
        installation_mode = str(
            getattr(back_panel.installation_mode, "value", back_panel.installation_mode)
        ).upper()
        if installation_mode == "GROOVED":
            offset = BackPanelRule.groove_offset
            new_z = base_height + offset
            new_height = max(cabinet_height - base_height - (2 * offset), 0.0)
        else:
            new_z = base_height + thickness
            new_height = max(cabinet_height - base_height - (2 * thickness), 0.0)
        back_panel = replace(
            back_panel,
            height_mm=new_height,
            position_mm=(
                back_panel.position_mm[0],
                cabinet_depth - back_panel.thickness_mm,
                new_z,
            ),
        )

    inner_width = bottom_panel.width_mm
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
    return replace(
        engineering_model,
        bottom_panel=bottom_panel,
        back_panel=back_panel,
        plinth_panels=plinth_panels,
    )


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
    back_thickness = float(getattr(cabinet.params, "back_thickness", 0.0) or 0.0)
    engineering_model = _enrich_toe_kick_engineering_placement(
        engineering_model,
        base_height=base_height,
        toe_kick_required=specification.toe_kick_required,
        back_thickness=back_thickness,
    )
    cabinet.engineering_model = engineering_model
    return cabinet
