from __future__ import annotations

from manufacturing.operation_instance import (
    ManufacturingOperationInstance,
    validate_operation_instance_contract,
)
from manufacturing.operation_realizer import (
    ManufacturingOperation,
    validate_manufacturing_operation_contract,
)


class ManufacturingOperationInstantiator:
    def instantiate(
        self,
        operation: ManufacturingOperation,
        instance_labels: tuple[str, ...],
        geometry_refs: tuple[str, ...] = (),
        faces: tuple[str, ...] = (),
    ) -> tuple[ManufacturingOperationInstance, ...]:
        validate_manufacturing_operation_contract(operation)

        if geometry_refs != () and len(geometry_refs) != len(instance_labels):
            raise ValueError("geometry_refs length must match instance_labels")
        if faces != () and len(faces) != len(instance_labels):
            raise ValueError("faces length must match instance_labels")

        instances = []
        for index, instance_label in enumerate(instance_labels):
            geometry_ref = geometry_refs[index] if geometry_refs else ""
            face = faces[index] if faces else ""
            instance = ManufacturingOperationInstance(
                operation_instance_item_id=f"{operation.operation_instance_id}::{instance_label}",
                parent_operation_instance_id=operation.operation_instance_id,
                operation_id=operation.operation_id,
                target_type=operation.target_type,
                target_id=operation.target_id,
                instance_label=instance_label,
                geometry_ref=geometry_ref,
                face=face,
                metadata={},
            )
            validate_operation_instance_contract(instance)
            instances.append(instance)

        return tuple(instances)
