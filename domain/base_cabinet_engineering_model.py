from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple

from domain.furniture_construction_model import CabinetConstructionModel
from shared.enums import DoorType


@dataclass(frozen=True)
class EngineeringPanelPlacement:
    role: str
    name: str
    width_mm: float
    depth_mm: float
    height_mm: float
    position_mm: Tuple[float, float, float]
    thickness_mm: float
    material: str


@dataclass(frozen=True)
class EngineeringShelfPlacement:
    name: str
    section_index: int
    section_id: str
    source_rule: str
    width_mm: float
    depth_mm: float
    thickness_mm: float
    position_mm: Tuple[float, float, float]


@dataclass(frozen=True)
class EngineeringDividerPlacement:
    name: str
    section_index: int
    section_id: str
    source_rule: str
    width_mm: float
    depth_mm: float
    height_mm: float
    position_mm: Tuple[float, float, float]


@dataclass(frozen=True)
class EngineeringDoorPlacement:
    name: str
    section_index: int
    section_id: str
    door_index: int
    source_rule: str
    x_mm: float
    y_mm: float
    z_mm: float
    width_mm: float
    height_mm: float
    thickness_mm: float
    door_type: DoorType
    hinge_side: str
    layer: int
    material: str


@dataclass(frozen=True)
class EngineeringDrawerBox:
    name: str
    section_index: int
    section_id: str
    drawer_index: int
    source_rule: str
    box_x_mm: float
    box_y_mm: float
    box_z_mm: float
    box_w_mm: float
    box_h_mm: float
    box_d_mm: float
    bottom_thickness_mm: float
    side_thickness_mm: float
    layer: int
    material: str


@dataclass(frozen=True)
class EngineeringDrawerFace:
    name: str
    section_index: int
    section_id: str
    drawer_index: int
    source_rule: str
    face_x_mm: float
    face_y_mm: float
    face_z_mm: float
    face_w_mm: float
    face_h_mm: float
    thickness_mm: float
    layer: int
    material: str


class BackPanelInstallationMode(str, Enum):
    GROOVED = "GROOVED"
    OVERLAY = "OVERLAY"
    RABBETED = "RABBETED"
    FLOATING = "FLOATING"


class BackPanelStrategy(str, Enum):
    FULL_CABINET = "FULL_CABINET"
    PER_SECTION = "PER_SECTION"
    OVERLAY = "OVERLAY"
    RABBETED = "RABBETED"


@dataclass(frozen=True)
class EngineeringBackPanel:
    role: str
    name: str
    width_mm: float
    depth_mm: float
    height_mm: float
    position_mm: Tuple[float, float, float]
    thickness_mm: float
    material: str
    installation_mode: BackPanelInstallationMode
    placement: str
    panel_strategy: BackPanelStrategy
    groove_depth_mm: float
    groove_width_mm: float
    source_rule: str


@dataclass(frozen=True)
class BaseCabinetEngineeringModel:
    construction_model: CabinetConstructionModel
    left_side_panel: EngineeringPanelPlacement
    right_side_panel: EngineeringPanelPlacement
    top_panel: EngineeringPanelPlacement
    bottom_panel: EngineeringPanelPlacement
    back_panel: Optional[EngineeringBackPanel]
    plinth_panels: Tuple[EngineeringPanelPlacement, ...] = field(default_factory=tuple)
    doors: Tuple[EngineeringDoorPlacement, ...] = field(default_factory=tuple)
    shelves: Tuple[EngineeringShelfPlacement, ...] = field(default_factory=tuple)
    dividers: Tuple[EngineeringDividerPlacement, ...] = field(default_factory=tuple)
    drawer_boxes: Tuple[EngineeringDrawerBox, ...] = field(default_factory=tuple)
    drawer_faces: Tuple[EngineeringDrawerFace, ...] = field(default_factory=tuple)


def map_back_panel_installation_mode(
    installation_mode,
) -> BackPanelInstallationMode:
    value = str(getattr(installation_mode, "value", installation_mode) or "").upper()
    if value == BackPanelInstallationMode.GROOVED.value:
        return BackPanelInstallationMode.GROOVED
    if value == BackPanelInstallationMode.OVERLAY.value:
        return BackPanelInstallationMode.OVERLAY
    if value == BackPanelInstallationMode.RABBETED.value:
        return BackPanelInstallationMode.RABBETED
    if value == BackPanelInstallationMode.FLOATING.value:
        return BackPanelInstallationMode.FLOATING
    raise ValueError(f"Unsupported back panel installation mode: {installation_mode!r}")


def map_back_panel_strategy(back_panel_type) -> BackPanelStrategy:
    value = str(getattr(back_panel_type, "value", back_panel_type) or "").upper()
    if value == "GROOVED":
        return BackPanelStrategy.FULL_CABINET
    if value == BackPanelStrategy.OVERLAY.value:
        return BackPanelStrategy.OVERLAY
    if value == BackPanelStrategy.RABBETED.value:
        return BackPanelStrategy.RABBETED
    if value == BackPanelStrategy.PER_SECTION.value:
        return BackPanelStrategy.PER_SECTION
    raise ValueError(f"Unsupported back panel strategy source: {back_panel_type!r}")


class BaseCabinetEngineeringModelBuilder:
    @staticmethod
    def build(construction_model: CabinetConstructionModel) -> BaseCabinetEngineeringModel:
        spec = construction_model.specification
        thickness = spec.material_thickness_mm
        width = spec.width_mm
        depth = spec.depth_mm
        inner_width = width - (2 * thickness)
        back_thickness = spec.back_panel_thickness_mm
        shelf_z = spec.height_mm / 2.0
        back_construction = construction_model.back_panel

        left_side = EngineeringPanelPlacement(
            role="SIDE_PANEL",
            name="Left Side",
            width_mm=thickness,
            depth_mm=depth,
            height_mm=spec.height_mm,
            position_mm=(0.0, 0.0, 0.0),
            thickness_mm=thickness,
            material="MDF_18",
        )
        right_side = EngineeringPanelPlacement(
            role="SIDE_PANEL",
            name="Right Side",
            width_mm=thickness,
            depth_mm=depth,
            height_mm=spec.height_mm,
            position_mm=(width - thickness, 0.0, 0.0),
            thickness_mm=thickness,
            material="MDF_18",
        )
        top_panel = EngineeringPanelPlacement(
            role="TOP_PANEL",
            name="Top",
            width_mm=inner_width,
            depth_mm=depth,
            height_mm=thickness,
            position_mm=(thickness, 0.0, spec.height_mm - thickness),
            thickness_mm=thickness,
            material="MDF_18",
        )
        bottom_panel = EngineeringPanelPlacement(
            role="BOTTOM_PANEL",
            name="Bottom",
            width_mm=inner_width,
            depth_mm=depth,
            height_mm=thickness,
            position_mm=(thickness, 0.0, 0.0),
            thickness_mm=thickness,
            material="MDF_18",
        )
        back_panel = None
        if back_construction is not None and str(getattr(spec, "back_panel_type", "") or "").upper() != "NONE":
            back_panel = EngineeringBackPanel(
                role="BACK_PANEL",
                name="Grooved Back",
                width_mm=inner_width,
                depth_mm=back_thickness,
                height_mm=spec.height_mm - (2 * thickness),
                position_mm=(thickness, depth - back_thickness, thickness),
                thickness_mm=back_thickness,
                material="HDF_3",
                installation_mode=map_back_panel_installation_mode(
                    back_construction.installation_mode
                ),
                placement=back_construction.placement,
                panel_strategy=map_back_panel_strategy(spec.back_panel_type),
                groove_depth_mm=back_construction.groove_depth_mm,
                groove_width_mm=back_construction.groove_width_mm,
                source_rule="ConstructionResolver",
            )

        shelves = tuple(
            EngineeringShelfPlacement(
                name=shelf.name,
                section_index=0,
                section_id="SEC-1",
                source_rule="ConstructionResolver",
                width_mm=shelf.width_mm,
                depth_mm=shelf.depth_mm,
                thickness_mm=shelf.thickness_mm,
                position_mm=(thickness, 0.0, shelf_z),
            )
            for shelf in construction_model.shelves
        )
        doors = tuple(
            EngineeringDoorPlacement(
                name=door.name,
                section_index=0,
                section_id=door.section_id,
                door_index=door.door_index,
                source_rule="ConstructionResolver",
                x_mm=door.position_mm[0],
                y_mm=door.position_mm[1],
                z_mm=door.position_mm[2],
                width_mm=door.width_mm,
                height_mm=door.height_mm,
                thickness_mm=door.thickness_mm,
                door_type=DoorType.from_string(door.door_type),
                hinge_side=door.hinge_side.value
                if hasattr(door.hinge_side, "value")
                else str(door.hinge_side),
                layer=0,
                material=left_side.material,
            )
            for door in construction_model.doors
        )
        drawer_boxes: Tuple[EngineeringDrawerBox, ...] = ()
        drawer_faces: Tuple[EngineeringDrawerFace, ...] = ()
        dividers: Tuple[EngineeringDividerPlacement, ...] = ()

        return BaseCabinetEngineeringModel(
            construction_model=construction_model,
            left_side_panel=left_side,
            right_side_panel=right_side,
            top_panel=top_panel,
            bottom_panel=bottom_panel,
            back_panel=back_panel,
            plinth_panels=(),
            doors=doors,
            shelves=shelves,
            dividers=dividers,
            drawer_boxes=drawer_boxes,
            drawer_faces=drawer_faces,
        )
