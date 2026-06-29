from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple

from domain.furniture_construction_model import CabinetConstructionModel


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
    width_mm: float
    depth_mm: float
    thickness_mm: float
    position_mm: Tuple[float, float, float]


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
    back_panel: EngineeringBackPanel
    shelves: Tuple[EngineeringShelfPlacement, ...] = field(default_factory=tuple)


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
                width_mm=shelf.width_mm,
                depth_mm=shelf.depth_mm,
                thickness_mm=shelf.thickness_mm,
                position_mm=(thickness, 0.0, shelf_z),
            )
            for shelf in construction_model.shelves
        )

        return BaseCabinetEngineeringModel(
            construction_model=construction_model,
            left_side_panel=left_side,
            right_side_panel=right_side,
            top_panel=top_panel,
            bottom_panel=bottom_panel,
            back_panel=back_panel,
            shelves=shelves,
        )
