from __future__ import annotations

from manufacturing.operation_requirement import (
    ManufacturingOperationRequirement,
    validate_operation_requirement_contract,
)
from manufacturing.operation_vocabulary import OperationId


class ManufacturingOperationRequirementBuilder:
    @staticmethod
    def _build_requirement(
        target_type: str,
        target_id: str,
        operation_id: OperationId,
        reason: str,
    ) -> ManufacturingOperationRequirement:
        requirement = ManufacturingOperationRequirement(
            requirement_id=f"{target_id}::{operation_id.value}",
            operation_id=operation_id,
            target_type=target_type,
            target_id=target_id,
            reason=reason,
            source="OperationRequirementBuilder",
        )
        validate_operation_requirement_contract(requirement)
        return requirement

    def build_for_panel(
        self,
        panel_id: str,
        needs_edge_band: bool = False,
        needs_assembly_holes: bool = False,
    ) -> tuple[ManufacturingOperationRequirement, ...]:
        requirements = []
        if needs_edge_band:
            requirements.append(
                self._build_requirement(
                    "Panel",
                    panel_id,
                    OperationId.EDGE_BAND,
                    "Panel requires edge banding.",
                )
            )
        if needs_assembly_holes:
            requirements.append(
                self._build_requirement(
                    "Panel",
                    panel_id,
                    OperationId.DRILL_ASSEMBLY_HOLES,
                    "Panel requires assembly holes.",
                )
            )
        return tuple(requirements)

    def build_for_door(
        self,
        door_id: str,
        needs_edge_band: bool = True,
        needs_hinges: bool = True,
        needs_handle: bool = False,
    ) -> tuple[ManufacturingOperationRequirement, ...]:
        requirements = []
        if needs_edge_band:
            requirements.append(
                self._build_requirement(
                    "Door",
                    door_id,
                    OperationId.EDGE_BAND,
                    "Door requires edge banding.",
                )
            )
        if needs_hinges:
            requirements.extend(
                (
                    self._build_requirement(
                        "Door",
                        door_id,
                        OperationId.DRILL_HINGE_CUP,
                        "Door requires hinge cup drilling.",
                    ),
                    self._build_requirement(
                        "Door",
                        door_id,
                        OperationId.DRILL_HINGE_SCREW_HOLES,
                        "Door requires hinge screw holes.",
                    ),
                    self._build_requirement(
                        "Door",
                        door_id,
                        OperationId.INSTALL_HINGE,
                        "Door requires hinge installation.",
                    ),
                )
            )
        if needs_handle:
            requirements.extend(
                (
                    self._build_requirement(
                        "Door",
                        door_id,
                        OperationId.DRILL_HANDLE_HOLES,
                        "Door requires handle holes.",
                    ),
                    self._build_requirement(
                        "Door",
                        door_id,
                        OperationId.INSTALL_HANDLE,
                        "Door requires handle installation.",
                    ),
                )
            )
        return tuple(requirements)

    def build_for_drawer(
        self,
        drawer_id: str,
        needs_slide: bool = True,
        needs_front: bool = True,
    ) -> tuple[ManufacturingOperationRequirement, ...]:
        requirements = []
        if needs_slide:
            requirements.extend(
                (
                    self._build_requirement(
                        "Drawer",
                        drawer_id,
                        OperationId.DRILL_DRAWER_SLIDE_HOLES,
                        "Drawer requires drawer slide holes.",
                    ),
                    self._build_requirement(
                        "Drawer",
                        drawer_id,
                        OperationId.INSTALL_DRAWER_SLIDE,
                        "Drawer requires drawer slide installation.",
                    ),
                )
            )
        if needs_front:
            requirements.append(
                self._build_requirement(
                    "Drawer",
                    drawer_id,
                    OperationId.INSTALL_DRAWER_FRONT,
                    "Drawer requires front installation.",
                )
            )
        return tuple(requirements)
