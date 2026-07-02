from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from domain.furniture_construction_model import CabinetConstructionModel
from domain.wall_cabinet_engineering_model import WallCabinetEngineeringModel


@dataclass(frozen=True)
class _PanelPlacement:
    role: str
    name: str
    width_mm: float
    depth_mm: float
    height_mm: float
    position_mm: Tuple[float, float, float]
    thickness_mm: float
    coordinate_meaning: str


@dataclass(frozen=True)
class _BackPanelPlacement:
    role: str
    name: str
    width_mm: float
    depth_mm: float
    height_mm: float
    position_mm: Tuple[float, float, float]
    thickness_mm: float
    coordinate_meaning: str
    installation_mode: str
    placement: str
    groove_depth_mm: float
    groove_width_mm: float


@dataclass(frozen=True)
class _LocalCoordinateSystem:
    origin_mm: Tuple[float, float, float]


@dataclass(frozen=True)
class _WallReferencePlane:
    reference_face: str
    offset_mm: float
    coordinate_meaning: str


@dataclass(frozen=True)
class _WallClearanceReference:
    reference_face: str
    required_clearance_mm: float
    coordinate_meaning: str


@dataclass(frozen=True)
class _WallMountReference:
    mount_index: int
    position_mm: Tuple[float, float, float]
    coordinate_meaning: str
    hardware_family: str
    wall_type: str
    max_load_kg: float
    required_clearance_mm: float


@dataclass(frozen=True)
class _WallPlacements:
    left_side_panel: _PanelPlacement
    right_side_panel: _PanelPlacement
    top_panel: _PanelPlacement
    bottom_panel: _PanelPlacement
    back_panel: _BackPanelPlacement
    cabinet_origin_mm: Tuple[float, float, float]
    local_coordinate_system: _LocalCoordinateSystem
    wall_reference_plane: _WallReferencePlane
    wall_clearance_reference: _WallClearanceReference
    wall_mount_reference_points: Tuple[_WallMountReference, ...]
    ordered_panel_keys: Tuple[str, ...]


def _panel_by_role(
    construction_model: CabinetConstructionModel,
    role: str,
) -> object:
    for panel in construction_model.panels:
        if panel.role == role:
            return panel
    raise ValueError(f"Missing required panel role: {role}")


def _build_panel_placement(panel) -> _PanelPlacement:
    return _PanelPlacement(
        role=panel.role,
        name=panel.name,
        width_mm=panel.width_mm,
        depth_mm=panel.thickness_mm if panel.role == "SIDE_PANEL" else panel.height_mm,
        height_mm=panel.height_mm if panel.role == "SIDE_PANEL" else panel.thickness_mm,
        position_mm=panel.position_mm,
        thickness_mm=panel.thickness_mm,
        coordinate_meaning="cabinet-local panel placement in millimetres",
    )


def _build_top_bottom_panel_placement(panel, cabinet_depth_mm: float) -> _PanelPlacement:
    return _PanelPlacement(
        role=panel.role,
        name=panel.name,
        width_mm=panel.width_mm,
        depth_mm=cabinet_depth_mm,
        height_mm=panel.height_mm,
        position_mm=panel.position_mm,
        thickness_mm=panel.thickness_mm,
        coordinate_meaning="cabinet-local panel placement in millimetres",
    )


def _build_back_panel_placement(
    construction_model: CabinetConstructionModel,
) -> _BackPanelPlacement:
    back_panel = construction_model.back_panel
    panel = back_panel.panel
    spec = construction_model.specification
    return _BackPanelPlacement(
        role=panel.role,
        name=panel.name,
        width_mm=spec.width_mm - (2 * spec.material_thickness_mm),
        depth_mm=spec.back_panel_thickness_mm,
        height_mm=spec.height_mm - (2 * spec.material_thickness_mm),
        position_mm=(
            spec.material_thickness_mm,
            spec.depth_mm - spec.back_panel_thickness_mm,
            spec.material_thickness_mm,
        ),
        thickness_mm=panel.thickness_mm,
        coordinate_meaning="cabinet-local back panel placement in millimetres",
        installation_mode=back_panel.installation_mode,
        placement=back_panel.placement,
        groove_depth_mm=back_panel.groove_depth_mm,
        groove_width_mm=back_panel.groove_width_mm,
    )


def _build_wall_mount_reference_points(
    engineering_model: WallCabinetEngineeringModel,
    construction_model: CabinetConstructionModel,
) -> Tuple[_WallMountReference, ...]:
    spec = construction_model.specification
    mount_count = max(spec.wall_mount_count, 0)
    if mount_count == 0:
        return ()

    if mount_count == 1:
        x_positions = (spec.width_mm / 2.0,)
    else:
        span = spec.width_mm / float(mount_count + 1)
        x_positions = tuple(span * (index + 1) for index in range(mount_count))

    z_position = max(spec.height_mm - spec.material_thickness_mm, 0.0)
    y_position = spec.depth_mm

    return tuple(
        _WallMountReference(
            mount_index=index,
            position_mm=(x_positions[index], y_position, z_position),
            coordinate_meaning="cabinet-local wall mount reference point in millimetres",
            hardware_family=engineering_model.suspension_hardware_family,
            wall_type=engineering_model.wall_type,
            max_load_kg=engineering_model.max_load_kg,
            required_clearance_mm=engineering_model.required_clearance_mm,
        )
        for index in range(mount_count)
    )


def build_wall_placements(
    engineering_model: WallCabinetEngineeringModel,
    construction_model: CabinetConstructionModel,
) -> _WallPlacements:
    spec = construction_model.specification
    left_side = _panel_by_role(construction_model, "SIDE_PANEL")
    side_panels = [panel for panel in construction_model.panels if panel.role == "SIDE_PANEL"]
    if len(side_panels) < 2:
        raise ValueError("Wall cabinet construction model requires two side panels")
    side_panels = sorted(side_panels, key=lambda panel: panel.position_mm)
    left_side = side_panels[0]
    right_side = side_panels[-1]
    top_panel = _panel_by_role(construction_model, "TOP_PANEL")
    bottom_panel = _panel_by_role(construction_model, "BOTTOM_PANEL")

    cabinet_origin = (0.0, 0.0, 0.0)
    wall_reference_plane = _WallReferencePlane(
        reference_face="rear_outer_face",
        offset_mm=spec.depth_mm,
        coordinate_meaning="cabinet-local wall reference plane offset in millimetres",
    )
    wall_clearance_reference = _WallClearanceReference(
        reference_face=wall_reference_plane.reference_face,
        required_clearance_mm=engineering_model.required_clearance_mm,
        coordinate_meaning="required wall clearance referenced in cabinet-local terms",
    )

    return _WallPlacements(
        left_side_panel=_build_panel_placement(left_side),
        right_side_panel=_build_panel_placement(right_side),
        top_panel=_build_top_bottom_panel_placement(top_panel, spec.depth_mm),
        bottom_panel=_build_top_bottom_panel_placement(bottom_panel, spec.depth_mm),
        back_panel=_build_back_panel_placement(construction_model),
        cabinet_origin_mm=cabinet_origin,
        local_coordinate_system=_LocalCoordinateSystem(origin_mm=cabinet_origin),
        wall_reference_plane=wall_reference_plane,
        wall_clearance_reference=wall_clearance_reference,
        wall_mount_reference_points=_build_wall_mount_reference_points(
            engineering_model,
            construction_model,
        ),
        ordered_panel_keys=(
            "left_side_panel",
            "right_side_panel",
            "top_panel",
            "bottom_panel",
            "back_panel",
        ),
    )
