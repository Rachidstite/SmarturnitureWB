from __future__ import annotations

from dataclasses import dataclass, field

from manufacturing.operation_realizer import ManufacturingOperation
from manufacturing.operation_vocabulary import OperationId


FORBIDDEN_INSTANCE_METADATA_KEYS = {
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
    "start_time",
    "end_time",
    "priority",
    "assigned_to",
}


@dataclass(frozen=True)
class ManufacturingOperationInstance:
    operation_instance_item_id: str
    parent_operation_instance_id: str
    operation_id: OperationId
    target_type: str
    target_id: str
    instance_label: str
    geometry_ref: str = ""
    face: str = ""
    metadata: dict = field(default_factory=dict)


def validate_operation_instance_contract(
    instance: ManufacturingOperationInstance,
) -> None:
    if not isinstance(instance.operation_id, OperationId):
        raise TypeError("operation_id must be an OperationId")
    if not instance.operation_instance_item_id:
        raise ValueError("operation_instance_item_id must be non-empty")
    if not instance.parent_operation_instance_id:
        raise ValueError("parent_operation_instance_id must be non-empty")
    if not instance.target_type:
        raise ValueError("target_type must be non-empty")
    if not instance.target_id:
        raise ValueError("target_id must be non-empty")
    if not instance.instance_label:
        raise ValueError("instance_label must be non-empty")
    if not isinstance(instance.metadata, dict):
        raise TypeError("metadata must be a dict")
    forbidden_keys = FORBIDDEN_INSTANCE_METADATA_KEYS.intersection(instance.metadata.keys())
    if forbidden_keys:
        raise ValueError(
            f"metadata contains forbidden execution/runtime keys: {sorted(forbidden_keys)}"
        )
