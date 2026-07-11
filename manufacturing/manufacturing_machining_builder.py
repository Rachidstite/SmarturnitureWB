from manufacturing.manufacturing_machining_report import (
    ManufacturingMachiningReport,
)


class ManufacturingMachiningBuilder:

    def build(self, package):
        items = [
            self._item(operation)
            for operation in package.machining_operations
        ]

        return ManufacturingMachiningReport(
            items=items,
            total_items=len(items),
            warnings=package.warnings,
        )

    @staticmethod
    def _item(operation):
        item = {
            "operation_type": operation.operation_type,
            "diameter": operation.diameter,
            "depth": operation.depth,
            "is_through": operation.is_through,
            "x": operation.x,
            "y": operation.y,
            "z": operation.z,
            "face": operation.face,
            "axis": operation.axis,
            "source": operation.source,
        }
        for key, value in (getattr(operation, "metadata", None) or {}).items():
            item.setdefault(key, value)
        return item
