from __future__ import annotations

from dataclasses import dataclass, field

from manufacturing.operation_vocabulary import OperationId


APPROVED_TARGET_TYPES = (
    "Panel",
    "Door",
    "Drawer",
    "DrawerFront",
    "Shelf",
    "BackPanel",
    "Cabinet",
    "CabinetSide",
    "Carcass",
    "Hardware",
    "Assembly",
)

FORBIDDEN_METADATA_KEYS = {
    "machine_id",
    "worker_id",
    "operator_id",
    "job_id",
    "queue_id",
    "duration",
    "cost",
    "schedule",
    "station",
    "gcode",
    "tool_id",
    "runtime_status",
    "execution_status",
}


@dataclass(frozen=True)
class ManufacturingOperationRequirement:
    requirement_id: str
    operation_id: OperationId
    target_type: str
    target_id: str
    reason: str
    source: str
    metadata: dict = field(default_factory=dict)


def validate_operation_requirement_contract(
    requirement: ManufacturingOperationRequirement,
) -> None:
    if not isinstance(requirement.operation_id, OperationId):
        raise TypeError("operation_id must be an OperationId")
    if not requirement.target_type:
        raise ValueError("target_type must be non-empty")
    if requirement.target_type not in APPROVED_TARGET_TYPES:
        raise ValueError("target_type must be a product/domain target")
    if not requirement.target_id:
        raise ValueError("target_id must be non-empty")
    if not isinstance(requirement.metadata, dict):
        raise TypeError("metadata must be a dict")
    forbidden_keys = FORBIDDEN_METADATA_KEYS.intersection(requirement.metadata.keys())
    if forbidden_keys:
        raise ValueError(
            f"metadata contains forbidden execution/runtime keys: {sorted(forbidden_keys)}"
        )
