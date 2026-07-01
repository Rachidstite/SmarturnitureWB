from __future__ import annotations

from domain.furniture_construction_model import (
    BackPanelConstruction,
    BackPanelType,
    CabinetConstructionModel,
    CabinetConstructionSpecification,
    ConstructionMethod,
    ConstructionValidationIssue,
    HardwareConstruction,
    JoineryConstruction,
    PanelConstruction,
    ShelfConstruction,
    ShelfOwnership,
    ValidationSeverity,
)
from domain.wall_cabinet_specification import WallCabinetSpecification


def build_wall_cabinet_construction_model(
    specification: WallCabinetSpecification,
) -> CabinetConstructionModel:
    construction_specification = CabinetConstructionSpecification(
        width_mm=specification.width_mm,
        height_mm=specification.height_mm,
        depth_mm=specification.depth_mm,
        material_thickness_mm=18.0,
        back_panel_thickness_mm=3.0,
        construction_method=ConstructionMethod.CONFIRMAT_OR_MINIFIX,
        back_panel_type=BackPanelType.GROOVED,
        door_count=specification.door_count,
        shelf_count=max(specification.shelf_count, 1),
        drawer_count=0,
        wall_mount_count=1,
    )

    left = PanelConstruction(
        role="SIDE_PANEL",
        name="Left Side",
        width_mm=18.0,
        height_mm=specification.height_mm,
        thickness_mm=18.0,
        material="MDF_18",
        position_mm=(0.0, 0.0, 0.0),
        purpose="Left carcass side panel for wall cabinet",
    )
    right = PanelConstruction(
        role="SIDE_PANEL",
        name="Right Side",
        width_mm=18.0,
        height_mm=specification.height_mm,
        thickness_mm=18.0,
        material="MDF_18",
        position_mm=(specification.width_mm - 18.0, 0.0, 0.0),
        purpose="Right carcass side panel for wall cabinet",
    )
    top = PanelConstruction(
        role="TOP_PANEL",
        name="Top",
        width_mm=specification.width_mm - 36.0,
        height_mm=18.0,
        thickness_mm=18.0,
        material="MDF_18",
        position_mm=(18.0, 0.0, specification.height_mm - 18.0),
        purpose="Top panel between side panels for wall cabinet",
    )
    bottom = PanelConstruction(
        role="BOTTOM_PANEL",
        name="Bottom",
        width_mm=specification.width_mm - 36.0,
        height_mm=18.0,
        thickness_mm=18.0,
        material="MDF_18",
        position_mm=(18.0, 0.0, 0.0),
        purpose="Bottom panel between side panels for wall cabinet",
    )

    back_panel = BackPanelConstruction(
        panel=PanelConstruction(
            role="BACK_PANEL",
            name="Wall Back",
            width_mm=specification.width_mm - 36.0,
            height_mm=specification.height_mm - 18.0,
            thickness_mm=3.0,
            material="HDF_3",
            position_mm=(18.0, specification.depth_mm - 3.0, 9.0),
            purpose="Wall cabinet rear panel",
        ),
        placement="Inside rear groove behind side/top/bottom panels",
        installation_mode="GROOVED" if specification.has_back_panel else "NONE",
        groove_depth_mm=8.0,
        groove_width_mm=3.2,
        allowed_details=(
            "groove_seating",
            "wall_mount",
            "rear_alignment",
        ),
        disallowed_details=() if specification.has_back_panel else ("back_panel_absent",),
    )

    shelves = tuple(
        ShelfConstruction(
            name=f"Shelf {index + 1}",
            width_mm=specification.width_mm - 36.0,
            depth_mm=specification.depth_mm - 50.0,
            thickness_mm=18.0,
            is_adjustable=True,
            shelf_pin_ownership=ShelfOwnership.SIDE_PANELS_ONLY,
            shelf_pin_row_count=2,
            fixed_or_adjustable="ADJUSTABLE",
        )
        for index in range(max(specification.shelf_count, 1))
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
            "wall_mount",
        ),
        hidden_details=(),
    )

    hardware = HardwareConstruction(
        hinge_family=specification.hinge_family,
        shelf_pin_family="SHELF_PIN_5MM",
        joinery_hardware_family="CONFIRMAT_OR_MINIFIX",
        manufacturing_ready_details=(
            "hinges",
            "shelf_pins",
            "wall_mount_hardware",
        ),
        prohibited_details=("drawer_hardware",),
    )

    validation_issues = ()
    if not specification.has_back_panel:
        validation_issues = (
            ConstructionValidationIssue(
                code="NO_BACK_PANEL",
                message="Wall cabinet specification has no back panel",
                severity=ValidationSeverity.WARNING,
                target="cabinet",
            ),
        )

    return CabinetConstructionModel(
        specification=construction_specification,
        panels=(left, right, top, bottom),
        back_panel=back_panel,
        doors=(),
        shelves=shelves,
        joinery=joinery,
        hardware=hardware,
        validation_issues=validation_issues,
        allowed_details=("groove_seating", "shelf_pins", "wall_mount"),
        disallowed_details=("drawer_hardware", "wall_mount_hardware"),
    )
