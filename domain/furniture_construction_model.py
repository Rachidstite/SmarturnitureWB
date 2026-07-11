from __future__ import annotations

from dataclasses import dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Dict, Tuple


class ConstructionMethod(str, Enum):
    CONFIRMAT = "CONFIRMAT"
    MINIFIX = "MINIFIX"
    CONFIRMAT_OR_MINIFIX = "CONFIRMAT_OR_MINIFIX"


class HingeSide(str, Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class ShelfOwnership(str, Enum):
    SIDE_PANELS_ONLY = "SIDE_PANELS_ONLY"


class BackPanelType(str, Enum):
    GROOVED = "GROOVED"


class ValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass(frozen=True)
class CabinetConstructionSpecification:
    width_mm: float
    height_mm: float
    depth_mm: float
    material_thickness_mm: float
    back_panel_thickness_mm: float
    door_count: int
    shelf_count: int
    construction_method: ConstructionMethod
    back_panel_type: BackPanelType
    drawer_count: int = 0
    wall_mount_count: int = 0


@dataclass(frozen=True)
class PanelConstruction:
    role: str
    name: str
    width_mm: float
    height_mm: float
    thickness_mm: float
    material: str
    position_mm: Tuple[float, float, float]
    purpose: str


@dataclass(frozen=True)
class BackPanelConstruction:
    panel: PanelConstruction
    placement: str
    installation_mode: str
    groove_depth_mm: float
    groove_width_mm: float
    allowed_details: Tuple[str, ...]
    disallowed_details: Tuple[str, ...]


@dataclass(frozen=True)
class DoorConstruction:
    name: str
    width_mm: float
    height_mm: float
    thickness_mm: float
    hinge_side: HingeSide
    hinge_count: int
    opening_direction: str
    hardware_family: str
    door_type: str = "Inset"
    identity: str = ""
    section_id: str = "SEC-1"
    door_index: int = 0
    position_mm: Tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass(frozen=True)
class ShelfConstruction:
    name: str
    width_mm: float
    depth_mm: float
    thickness_mm: float
    is_adjustable: bool
    shelf_pin_ownership: ShelfOwnership
    shelf_pin_row_count: int
    fixed_or_adjustable: str


@dataclass(frozen=True)
class JoineryConstruction:
    method: ConstructionMethod
    primary_connector: str
    secondary_connector: str
    visible_details: Tuple[str, ...]
    hidden_details: Tuple[str, ...]


@dataclass(frozen=True)
class HardwareConstruction:
    hinge_family: str
    shelf_pin_family: str
    joinery_hardware_family: str
    manufacturing_ready_details: Tuple[str, ...]
    prohibited_details: Tuple[str, ...]


@dataclass(frozen=True)
class ConstructionValidationIssue:
    code: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    target: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CabinetConstructionModel:
    specification: CabinetConstructionSpecification
    panels: Tuple[PanelConstruction, ...]
    back_panel: BackPanelConstruction
    doors: Tuple[DoorConstruction, ...]
    shelves: Tuple[ShelfConstruction, ...]
    joinery: JoineryConstruction
    hardware: HardwareConstruction
    validation_issues: Tuple[ConstructionValidationIssue, ...] = ()
    allowed_details: Tuple[str, ...] = ()
    disallowed_details: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return _serialize(self)

    @staticmethod
    def reference_base_cabinet() -> "CabinetConstructionModel":
        spec = CabinetConstructionSpecification(
            width_mm=800.0,
            height_mm=720.0,
            depth_mm=560.0,
            material_thickness_mm=18.0,
            back_panel_thickness_mm=3.0,
            door_count=2,
            shelf_count=1,
            construction_method=ConstructionMethod.CONFIRMAT_OR_MINIFIX,
            back_panel_type=BackPanelType.GROOVED,
            drawer_count=0,
            wall_mount_count=0,
        )

        left_side = PanelConstruction(
            role="SIDE_PANEL",
            name="Left Side",
            width_mm=560.0,
            height_mm=720.0,
            thickness_mm=18.0,
            material="MDF_18",
            position_mm=(0.0, 0.0, 0.0),
            purpose="Primary carcass side",
        )
        right_side = PanelConstruction(
            role="SIDE_PANEL",
            name="Right Side",
            width_mm=560.0,
            height_mm=720.0,
            thickness_mm=18.0,
            material="MDF_18",
            position_mm=(782.0, 0.0, 0.0),
            purpose="Primary carcass side",
        )
        top = PanelConstruction(
            role="TOP_PANEL",
            name="Top",
            width_mm=764.0,
            height_mm=18.0,
            thickness_mm=18.0,
            material="MDF_18",
            position_mm=(18.0, 0.0, 702.0),
            purpose="Carcass top",
        )
        bottom = PanelConstruction(
            role="BOTTOM_PANEL",
            name="Bottom",
            width_mm=764.0,
            height_mm=18.0,
            thickness_mm=18.0,
            material="MDF_18",
            position_mm=(18.0, 0.0, 80.0),
            purpose="Carcass bottom",
        )

        back_panel = BackPanelConstruction(
            panel=PanelConstruction(
                role="BACK_PANEL",
                name="Grooved Back",
                width_mm=764.0,
                height_mm=602.0,
                thickness_mm=3.0,
                material="HDF_3",
                position_mm=(18.0, 557.0, 98.0),
                purpose="Grooved back panel seated inside the carcass",
            ),
            placement="Inside rear groove behind side/top/bottom panels",
            installation_mode="GROOVED",
            groove_depth_mm=8.0,
            groove_width_mm=3.2,
            allowed_details=(
                "groove_seating",
                "rear_alignment",
                "structural_racking_support",
            ),
            disallowed_details=(
                "floating_back_panel",
                "surface_overlay_back_panel",
                "drawer_geometry",
            ),
        )

        doors = (
            DoorConstruction(
                name="Left Door",
                width_mm=380.0,
                height_mm=620.0,
                thickness_mm=18.0,
                hinge_side=HingeSide.LEFT,
                hinge_count=2,
                opening_direction="LEFT",
                hardware_family="HINGE_BLUM_110_V1",
                door_type="Inset",
                identity="SEC-1_DOOR_1",
                section_id="SEC-1",
                door_index=0,
                position_mm=(18.0, 2.0, 98.0),
            ),
            DoorConstruction(
                name="Right Door",
                width_mm=380.0,
                height_mm=620.0,
                thickness_mm=18.0,
                hinge_side=HingeSide.RIGHT,
                hinge_count=2,
                opening_direction="RIGHT",
                hardware_family="HINGE_BLUM_110_V1",
                door_type="Inset",
                identity="SEC-1_DOOR_2",
                section_id="SEC-1",
                door_index=1,
                position_mm=(402.0, 2.0, 98.0),
            ),
        )

        shelves = (
            ShelfConstruction(
                name="Adjustable Shelf",
                width_mm=764.0,
                depth_mm=500.0,
                thickness_mm=18.0,
                is_adjustable=True,
                shelf_pin_ownership=ShelfOwnership.SIDE_PANELS_ONLY,
                shelf_pin_row_count=2,
                fixed_or_adjustable="ADJUSTABLE",
            ),
        )

        joinery = JoineryConstruction(
            method=ConstructionMethod.CONFIRMAT_OR_MINIFIX,
            primary_connector="CONFIRMAT_50_V1",
            secondary_connector="MINIFIX_15_V1",
            visible_details=(
                "confirmat_joinery",
                "minifix_joinery",
                "grooved_back_panel",
                "shelf_pin_rows",
            ),
            hidden_details=(
                "drawers",
                "wall_mount",
            ),
        )

        hardware = HardwareConstruction(
            hinge_family="HINGE_BLUM_110_V1",
            shelf_pin_family="SHELF_PIN_5MM",
            joinery_hardware_family="CONFIRMAT_OR_MINIFIX",
            manufacturing_ready_details=(
                "hinges",
                "shelf_pins",
                "confirmat_joinery",
                "minifix_joinery",
            ),
            prohibited_details=(
                "drawer_hardware",
                "wall_mount_hardware",
            ),
        )

        return CabinetConstructionModel(
            specification=spec,
            panels=(left_side, right_side, top, bottom),
            back_panel=back_panel,
            doors=doors,
            shelves=shelves,
            joinery=joinery,
            hardware=hardware,
            validation_issues=(
                ConstructionValidationIssue(
                    code="NO_DRAWERS",
                    message="Reference cabinet explicitly excludes drawers.",
                    severity=ValidationSeverity.INFO,
                    target="cabinet",
                ),
                ConstructionValidationIssue(
                    code="NO_WALL_MOUNT",
                    message="Reference cabinet explicitly excludes wall mount hardware.",
                    severity=ValidationSeverity.INFO,
                    target="cabinet",
                ),
            ),
            allowed_details=(
                "grooved_back_panel",
                "left_right_doors",
                "adjustable_shelf",
                "side_panel_shelf_pin_rows",
                "confirmat_or_minifix_joinery",
            ),
            disallowed_details=(
                "drawers",
                "wall_mount",
                "floating_holes",
                "visual_pruning",
            ),
        )


def _serialize(value):
    if is_dataclass(value):
        return {
            field.name: _serialize(getattr(value, field.name))
            for field in value.__dataclass_fields__.values()
        }
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return tuple(_serialize(item) for item in value)
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value
