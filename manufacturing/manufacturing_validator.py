class ManufacturingValidator:

    def validate(self, package):
        warnings = []

        for panel in package.panels:
            if panel.width <= 0:
                warnings.append("Invalid panel width")
            if panel.height <= 0:
                warnings.append("Invalid panel height")
            if panel.thickness <= 0:
                warnings.append("Invalid panel thickness")

        for material in package.materials:
            if not material.name:
                warnings.append("Missing material name")

        operations = package.machining_operations + package.edge_operations
        for operation in operations:
            if not operation.operation_type:
                warnings.append("Missing operation type")

        return warnings
