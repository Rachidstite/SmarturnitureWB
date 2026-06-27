from __future__ import annotations

from dataclasses import dataclass, field

from manufacturing.operation_requirement import (
    ManufacturingOperationRequirement,
    validate_operation_requirement_contract,
)
from manufacturing.operation_vocabulary import OperationId


FORBIDDEN_OPERATION_METADATA_KEYS = {
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
class ManufacturingOperation:
    operation_instance_id: str
    requirement_id: str
    operation_id: OperationId
    target_type: str
    target_id: str
    source_requirement: ManufacturingOperationRequirement
    metadata: dict = field(default_factory=dict)


def validate_manufacturing_operation_contract(operation: ManufacturingOperation) -> None:
    if not isinstance(operation.operation_id, OperationId):
        raise TypeError("operation_id must be an OperationId")
    if not operation.requirement_id:
        raise ValueError("requirement_id must be non-empty")
    if not operation.operation_instance_id:
        raise ValueError("operation_instance_id must be non-empty")
    if not operation.target_type:
        raise ValueError("target_type must be non-empty")
    if not operation.target_id:
        raise ValueError("target_id must be non-empty")
    if not isinstance(operation.source_requirement, ManufacturingOperationRequirement):
        raise TypeError("source_requirement must be a ManufacturingOperationRequirement")
    if not isinstance(operation.metadata, dict):
        raise TypeError("metadata must be a dict")
    forbidden_keys = FORBIDDEN_OPERATION_METADATA_KEYS.intersection(operation.metadata.keys())
    if forbidden_keys:
        raise ValueError(
            f"metadata contains forbidden execution/runtime keys: {sorted(forbidden_keys)}"
        )


class ManufacturingOperationRealizer:
    @staticmethod
    def _realize_requirement(
        requirement: ManufacturingOperationRequirement,
    ) -> ManufacturingOperation:
        operation = ManufacturingOperation(
            operation_instance_id=f"{requirement.requirement_id}::operation",
            requirement_id=requirement.requirement_id,
            operation_id=requirement.operation_id,
            target_type=requirement.target_type,
            target_id=requirement.target_id,
            source_requirement=requirement,
            metadata={},
        )
        validate_manufacturing_operation_contract(operation)
        return operation

    def realize(
        self,
        requirements: tuple[ManufacturingOperationRequirement, ...],
    ) -> tuple[ManufacturingOperation, ...]:
        operations = []
        for requirement in requirements:
            validate_operation_requirement_contract(requirement)
            operations.append(self._realize_requirement(requirement))
        return tuple(operations)
