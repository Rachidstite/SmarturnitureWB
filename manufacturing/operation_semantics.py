"""dependency_hints are semantic dependency hints only.
They are not execution order, scheduling order, workflow steps, or runtime dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from manufacturing.operation_vocabulary import OPERATION_CATEGORY_BY_ID, OperationId


class OperationIdempotency(str, Enum):
    REPEATABLE = "REPEATABLE"
    CONDITIONALLY_REPEATABLE = "CONDITIONALLY_REPEATABLE"
    NOT_REPEATABLE = "NOT_REPEATABLE"


class OperationReversibility(str, Enum):
    REVERSIBLE = "REVERSIBLE"
    PARTIALLY_REVERSIBLE = "PARTIALLY_REVERSIBLE"
    DESTRUCTIVE_REVERSAL = "DESTRUCTIVE_REVERSAL"
    IRREVERSIBLE = "IRREVERSIBLE"


@dataclass(frozen=True)
class OperationSemantics:
    operation_id: OperationId
    target_types: tuple[str, ...]
    intent: str
    input_state: tuple[str, ...]
    output_state: tuple[str, ...]
    required_manufacturing_capabilities: tuple[str, ...]
    dependency_hints: tuple[str, ...]
    quality_meaning: str
    idempotency: OperationIdempotency
    reversibility: OperationReversibility


OPERATION_SEMANTICS_V1: dict[OperationId, OperationSemantics] = {
    OperationId.CUT_TO_SIZE: OperationSemantics(
        operation_id=OperationId.CUT_TO_SIZE,
        target_types=("Panel", "Shelf"),
        intent="Bring a part to the planned size.",
        input_state=("Oversized stock part with a defined cut plan.",),
        output_state=("Sized part that matches the planned dimensions.",),
        required_manufacturing_capabilities=("Dimension control", "Edge control"),
        dependency_hints=("Size plan available",),
        quality_meaning="Size matches the defined plan.",
        idempotency=OperationIdempotency.NOT_REPEATABLE,
        reversibility=OperationReversibility.IRREVERSIBLE,
    ),
    OperationId.EDGE_BAND: OperationSemantics(
        operation_id=OperationId.EDGE_BAND,
        target_types=("Panel", "Shelf"),
        intent="Cover exposed edges with the planned banding.",
        input_state=("Part with exposed edges ready for coverage.",),
        output_state=("Part with covered edges.",),
        required_manufacturing_capabilities=("Edge coverage", "Bond application"),
        dependency_hints=("Edge exposed",),
        quality_meaning="Exposed edges are covered as intended.",
        idempotency=OperationIdempotency.NOT_REPEATABLE,
        reversibility=OperationReversibility.DESTRUCTIVE_REVERSAL,
    ),
    OperationId.DRILL_HINGE_CUP: OperationSemantics(
        operation_id=OperationId.DRILL_HINGE_CUP,
        target_types=("Door", "DoorFront", "Panel"),
        intent="Create the cup recess for a hinge.",
        input_state=("Part marked for hinge cup placement.",),
        output_state=("Part with hinge cup recess formed.",),
        required_manufacturing_capabilities=("Hole creation", "Depth control"),
        dependency_hints=("Hinge location defined",),
        quality_meaning="Cup recess matches the planned position and depth.",
        idempotency=OperationIdempotency.CONDITIONALLY_REPEATABLE,
        reversibility=OperationReversibility.PARTIALLY_REVERSIBLE,
    ),
    OperationId.INSTALL_DRAWER_SLIDE: OperationSemantics(
        operation_id=OperationId.INSTALL_DRAWER_SLIDE,
        target_types=("Drawer", "CabinetSide"),
        intent="Attach the slide hardware to the prepared part.",
        input_state=("Part prepared for slide attachment.",),
        output_state=("Part with slide hardware attached.",),
        required_manufacturing_capabilities=("Attachment alignment", "Fastener application"),
        dependency_hints=("Slide locations prepared",),
        quality_meaning="Slide hardware sits in the planned position.",
        idempotency=OperationIdempotency.NOT_REPEATABLE,
        reversibility=OperationReversibility.PARTIALLY_REVERSIBLE,
    ),
    OperationId.ASSEMBLE_CARCASS: OperationSemantics(
        operation_id=OperationId.ASSEMBLE_CARCASS,
        target_types=("Cabinet", "Carcass"),
        intent="Combine the structural parts into the cabinet body.",
        input_state=("Prepared structural parts ready for assembly.",),
        output_state=("Assembled cabinet body.",),
        required_manufacturing_capabilities=("Part relation control", "Joint closure"),
        dependency_hints=("All structural parts prepared",),
        quality_meaning="Body geometry matches the intended structure.",
        idempotency=OperationIdempotency.CONDITIONALLY_REPEATABLE,
        reversibility=OperationReversibility.PARTIALLY_REVERSIBLE,
    ),
    OperationId.INSTALL_DRAWER_FRONT: OperationSemantics(
        operation_id=OperationId.INSTALL_DRAWER_FRONT,
        target_types=("Drawer", "DrawerFront"),
        intent="Attach the front element to the drawer body.",
        input_state=("Drawer body and front prepared for joining.",),
        output_state=("Drawer with front attached.",),
        required_manufacturing_capabilities=("Front alignment", "Joint closure"),
        dependency_hints=("Drawer box complete",),
        quality_meaning="Front sits flush with the drawer body.",
        idempotency=OperationIdempotency.NOT_REPEATABLE,
        reversibility=OperationReversibility.PARTIALLY_REVERSIBLE,
    ),
    OperationId.INSPECT_SHELF_SUPPORT: OperationSemantics(
        operation_id=OperationId.INSPECT_SHELF_SUPPORT,
        target_types=("Shelf", "Cabinet"),
        intent="Verify that the shelf support state is acceptable.",
        input_state=("Shelf and support points in assembled state.",),
        output_state=("Shelf support assessment recorded.",),
        required_manufacturing_capabilities=("Support assessment", "Measurement review"),
        dependency_hints=("Shelf installed",),
        quality_meaning="Support state meets the expected standard.",
        idempotency=OperationIdempotency.REPEATABLE,
        reversibility=OperationReversibility.REVERSIBLE,
    ),
    OperationId.INSPECT_HARDWARE_ALIGNMENT: OperationSemantics(
        operation_id=OperationId.INSPECT_HARDWARE_ALIGNMENT,
        target_types=("Hardware", "Assembly"),
        intent="Verify that installed hardware matches the planned position.",
        input_state=("Hardware installed or prepared for review.",),
        output_state=("Hardware alignment assessment recorded.",),
        required_manufacturing_capabilities=("Alignment review", "Position comparison"),
        dependency_hints=("Hardware installed",),
        quality_meaning="Hardware position matches the defined standard.",
        idempotency=OperationIdempotency.REPEATABLE,
        reversibility=OperationReversibility.REVERSIBLE,
    ),
}


def validate_semantics_registry() -> None:
    for operation_id, semantics in OPERATION_SEMANTICS_V1.items():
        if operation_id not in OPERATION_CATEGORY_BY_ID:
            raise ValueError(f"Unknown operation id: {operation_id}")
        if semantics.operation_id != operation_id:
            raise ValueError(f"Operation id mismatch for {operation_id}")
