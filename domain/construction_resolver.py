from __future__ import annotations

from domain.base_cabinet_specification import BaseCabinetSpecification
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


class ConstructionResolver:
    @staticmethod
    def resolve(
        specification: BaseCabinetSpecification,
    ) -> CabinetConstructionModel:
        construction_spec = CabinetConstructionSpecification(
            width_mm=specification.width_mm,
            height_mm=specification.height_mm,
            depth_mm=specification.depth_mm,
            material_thickness_mm=18.0,
            back_panel_thickness_mm=3.0,
            door_count=specification.door_count,
            shelf_count=specification.shelf_count,
            construction_method=ConstructionMethod.CONFIRMAT_OR_MINIFIX,
            back_panel_type=BackPanelType.GROOVED
            if specification.has_back_panel
            else BackPanelType.GROOVED,
            drawer_count=0,
            wall_mount_count=0,
        )

        thickness = construction_spec.material_thickness_mm
        inner_width = construction_spec.width_mm - (2 * thickness)

        left_side = PanelConstruction(
            role="SIDE_PANEL",
            name="Left Side",
            width_mm=thickness,
            height_mm=construction_spec.height_mm,
            thickness_mm=thickness,
            material="MDF_18",
            position_mm=(0.0, 0.0, 0.0),
            purpose="Left carcass side",
        )
        right_side = PanelConstruction(
            role="SIDE_PANEL",
            name="Right Side",
            width_mm=thickness,
            height_mm=construction_spec.height_mm,
            thickness_mm=thickness,
            material="MDF_18",
            position_mm=(0.0, 0.0, 0.0),
            purpose="Right carcass side",
        )
        top = PanelConstruction(
            role="TOP_PANEL",
            name="Top",
            width_mm=inner_width,
            height_mm=thickness,
            thickness_mm=thickness,
            material="MDF_18",
            position_mm=(0.0, 0.0, 0.0),
            purpose="Top panel between side panels",
        )
        bottom = PanelConstruction(
            role="BOTTOM_PANEL",
            name="Bottom",
            width_mm=inner_width,
            height_mm=thickness,
            thickness_mm=thickness,
            material="MDF_18",
            position_mm=(0.0, 0.0, 0.0),
            purpose="Bottom panel between side panels",
        )
        back_panel = BackPanelConstruction(
            panel=PanelConstruction(
                role="BACK_PANEL",
                name="Grooved Back",
                width_mm=inner_width,
                height_mm=construction_spec.height_mm - (2 * thickness),
                thickness_mm=3.0,
                material="HDF_3",
                position_mm=(0.0, 0.0, 0.0),
                purpose="Grooved back panel seated behind the carcass panels",
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

        shelves = tuple(
            ShelfConstruction(
                name=f"Adjustable Shelf {index + 1}",
                width_mm=inner_width,
                depth_mm=max(construction_spec.depth_mm - 60.0, 0.0),
                thickness_mm=thickness,
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
                "side_panel_shelf_pin_rows",
            ),
            hidden_details=(),
        )

        hardware = HardwareConstruction(
            hinge_family=specification.hinge_family,
            shelf_pin_family="SHELF_PIN_5MM",
            joinery_hardware_family="CONFIRMAT_OR_MINIFIX",
            manufacturing_ready_details=(
                "confirmat_joinery",
                "minifix_joinery",
                "shelf_pins",
            ),
            prohibited_details=(
                "drawer_hardware",
                "wall_mount_hardware",
            ),
        )

        validation_issues = ()
        if not specification.has_back_panel:
            validation_issues = (
                ConstructionValidationIssue(
                    code="NO_BACK_PANEL",
                    message="Reference design expects a grooved back panel.",
                    severity=ValidationSeverity.WARNING,
                    target="cabinet",
                ),
            )

        return CabinetConstructionModel(
            specification=construction_spec,
            panels=(left_side, right_side, top, bottom),
            back_panel=back_panel,
            doors=(),
            shelves=shelves,
            joinery=joinery,
            hardware=hardware,
            validation_issues=validation_issues,
            allowed_details=(
                "left_side_panel",
                "right_side_panel",
                "top_panel",
                "bottom_panel",
                "grooved_back_panel",
                "adjustable_shelf",
                "side_panel_shelf_pin_rows",
            ),
            disallowed_details=(
                "drawers",
                "door_geometry",
                "wall_mount",
                "floating_holes",
            ),
        )
