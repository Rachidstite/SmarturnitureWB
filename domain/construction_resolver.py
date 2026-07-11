from __future__ import annotations

from core.material_manager import MaterialManager
from domain.base_cabinet_specification_adapter import BaseCabinetSpecificationAdapter
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.front_layout import FrontLayoutEngine, OpeningContext
from domain.furniture_construction_model import (
    BackPanelConstruction,
    BackPanelType,
    CabinetConstructionModel,
    CabinetConstructionSpecification,
    ConstructionMethod,
    ConstructionValidationIssue,
    DoorConstruction,
    HingeSide,
    HardwareConstruction,
    JoineryConstruction,
    PanelConstruction,
    ShelfConstruction,
    ShelfOwnership,
    ValidationSeverity,
)
from domain.system32 import System32Engine
from shared.enums import DoorType


class ConstructionResolver:
    @staticmethod
    def _resolve_doors(
        specification: BaseCabinetSpecification,
        construction_spec: CabinetConstructionSpecification,
        *,
        inner_width: float,
    ) -> tuple[DoorConstruction, ...]:
        door_count = max(int(getattr(specification, "door_count", 0) or 0), 0)
        if door_count <= 0:
            return ()

        adapter_result = BaseCabinetSpecificationAdapter.adapt(specification)
        params = adapter_result.cabinet_params
        section_config = (getattr(params, "sec_data", {}) or {}).get(0)
        if section_config is None:
            return ()

        door_type = DoorType.from_string(getattr(section_config, "doors", "None"))
        if door_type == DoorType.NONE:
            return ()

        mat = MaterialManager()
        base_height = float(getattr(params, "base_height", 0.0) or 0.0)
        if not specification.toe_kick_required:
            base_height = 0.0

        available_height = (
            construction_spec.height_mm
            - base_height
            - (2 * construction_spec.material_thickness_mm)
        )
        door_height = available_height - mat.door_top_gap - mat.door_bottom_gap
        if door_height <= 0.0:
            return ()
        door_zone_z = (
            base_height
            + construction_spec.material_thickness_mm
            + mat.door_bottom_gap
        )

        thickness = construction_spec.material_thickness_mm
        doors = []

        if door_type.is_overlay():
            opening = OpeningContext(
                identity="SEC_0",
                width=inner_width,
                height=door_height,
                local_x=thickness,
                local_y=door_zone_z,
                left_divider_thickness=thickness,
                right_divider_thickness=thickness,
                top_divider_thickness=thickness,
                bottom_divider_thickness=thickness,
                left_overlay=mat.side_overlay,
                right_overlay=mat.side_overlay,
            )
            resolved_fronts = FrontLayoutEngine.generate_doors_for_opening(
                opening,
                door_count,
            )
            front_y = -thickness + mat.overlay_setback
            for door_index, front in enumerate(resolved_fronts):
                hinge_positions = System32Engine.hinge_positions(front.height)
                hinge_side = HingeSide.LEFT if front.hinge_side == "LEFT" else HingeSide.RIGHT
                doors.append(
                    DoorConstruction(
                        name=f"Door {door_index + 1}",
                        width_mm=front.width,
                        height_mm=front.height,
                        thickness_mm=thickness,
                        hinge_side=hinge_side,
                        hinge_count=len(hinge_positions),
                        opening_direction=hinge_side.value,
                        hardware_family=specification.hinge_family,
                        door_type="Overlay",
                        identity=f"SEC-1_DOOR_{door_index + 1}",
                        section_id="SEC-1",
                        door_index=door_index,
                        position_mm=(front.local_x, front_y, door_zone_z),
                    )
                )
        elif door_type.is_sliding():
            overlap = mat.sliding_overlap
            side_extra = mat.sliding_side_extra
            total_width = inner_width + (2 * side_extra)
            door_width = (
                (total_width + ((door_count - 1) * overlap)) / door_count
                if door_count > 1
                else total_width
            )
            track_step = door_width - overlap
            start_x = thickness - side_extra
            for door_index in range(door_count):
                hinge_positions = System32Engine.hinge_positions(door_height)
                doors.append(
                    DoorConstruction(
                        name=f"Door {door_index + 1}",
                        width_mm=door_width,
                        height_mm=door_height,
                        thickness_mm=thickness,
                        hinge_side=HingeSide.LEFT,
                        hinge_count=len(hinge_positions),
                        opening_direction=HingeSide.LEFT.value,
                        hardware_family=specification.hinge_family,
                        door_type="Sliding",
                        identity=f"SEC-1_DOOR_{door_index + 1}",
                        section_id="SEC-1",
                        door_index=door_index,
                        position_mm=(start_x + (door_index * track_step), 0.0, door_zone_z),
                    )
                )
        else:
            side_clearance = mat.inset_side_clearance
            center_gap = mat.door_side_gap
            available_width = inner_width - (2 * side_clearance) - ((door_count - 1) * center_gap)
            door_width = available_width / door_count if door_count > 1 else available_width
            start_x = thickness + side_clearance
            front_y = mat.clearance
            for door_index in range(door_count):
                hinge_side = HingeSide.LEFT if door_index == 0 else HingeSide.RIGHT
                hinge_positions = System32Engine.hinge_positions(door_height)
                doors.append(
                    DoorConstruction(
                        name=f"Door {door_index + 1}",
                        width_mm=door_width,
                        height_mm=door_height,
                        thickness_mm=thickness,
                        hinge_side=hinge_side,
                        hinge_count=len(hinge_positions),
                        opening_direction=hinge_side.value,
                        hardware_family=specification.hinge_family,
                        door_type="Inset",
                        identity=f"SEC-1_DOOR_{door_index + 1}",
                        section_id="SEC-1",
                        door_index=door_index,
                        position_mm=(
                            start_x + (door_index * (door_width + center_gap)),
                            front_y,
                            door_zone_z,
                        ),
                    )
                )

        return tuple(doors)

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
            else "NONE",
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
        back_panel = None
        if specification.has_back_panel:
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

        doors = ConstructionResolver._resolve_doors(
            specification,
            construction_spec,
            inner_width=inner_width,
        )

        return CabinetConstructionModel(
            specification=construction_spec,
            panels=(left_side, right_side, top, bottom),
            back_panel=back_panel,
            doors=doors,
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
                "door_geometry",
            ),
            disallowed_details=(
                "drawers",
                "wall_mount",
                "floating_holes",
            ),
        )
