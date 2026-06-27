from __future__ import annotations

from dataclasses import dataclass, field


ALLOWED_RELATIONSHIP_TYPES = (
    "REQUIRES_PREPARED_GEOMETRY",
    "REQUIRES_HARDWARE_PREPARATION",
    "REQUIRES_JOINERY_PREPARATION",
    "REQUIRES_ASSEMBLED_TARGET",
    "REQUIRES_INSPECTION_INPUT",
)

FORBIDDEN_LINK_METADATA_KEYS = {
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
class ManufacturingOperationLink:
    link_id: str
    predecessor_instance_id: str
    successor_instance_id: str
    relationship_type: str
    reason: str
    metadata: dict = field(default_factory=dict)


def validate_operation_link_contract(link: ManufacturingOperationLink) -> None:
    if not link.predecessor_instance_id:
        raise ValueError("predecessor_instance_id must be non-empty")
    if not link.successor_instance_id:
        raise ValueError("successor_instance_id must be non-empty")
    if not link.link_id:
        raise ValueError("link_id must be non-empty")
    if link.relationship_type not in ALLOWED_RELATIONSHIP_TYPES:
        raise ValueError("relationship_type must be an allowed semantic relationship")
    if not isinstance(link.metadata, dict):
        raise TypeError("metadata must be a dict")
    forbidden_keys = FORBIDDEN_LINK_METADATA_KEYS.intersection(link.metadata.keys())
    if forbidden_keys:
        raise ValueError(f"metadata contains forbidden keys: {sorted(forbidden_keys)}")
