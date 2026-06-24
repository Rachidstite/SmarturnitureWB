from manufacturing.manufacturing_simulation_report import (
    ManufacturingSimulationReport,
)


class ManufacturingSimulationBuilder:

    def build(self, manufacturing_package):
        panels = getattr(manufacturing_package, "panels", []) or []
        machining_operations = (
            getattr(manufacturing_package, "machining_operations", []) or []
        )
        edge_operations = (
            getattr(manufacturing_package, "edge_operations", []) or []
        )
        warnings = getattr(manufacturing_package, "warnings", []) or []

        panel_count = len(panels)
        machining_operation_count = len(machining_operations)
        edge_operation_count = len(edge_operations)
        drilling_operation_count = sum(
            1
            for operation in machining_operations
            if self._is_drilling_operation(operation)
        )
        assembly_operation_count = panel_count

        estimated_cnc_minutes = machining_operation_count * 1.5
        estimated_edge_banding_minutes = edge_operation_count * 0.75
        estimated_assembly_minutes = panel_count * 3.0
        estimated_total_factory_minutes = (
            estimated_cnc_minutes
            + estimated_edge_banding_minutes
            + estimated_assembly_minutes
        )

        if warnings:
            simulation_status = "REVIEW"
            simulation_recommendation = (
                "Review manufacturing package before production"
            )
        else:
            simulation_status = "READY"
            simulation_recommendation = ""

        return ManufacturingSimulationReport(
            panel_count=panel_count,
            machining_operation_count=machining_operation_count,
            edge_operation_count=edge_operation_count,
            drilling_operation_count=drilling_operation_count,
            assembly_operation_count=assembly_operation_count,
            estimated_cnc_minutes=estimated_cnc_minutes,
            estimated_edge_banding_minutes=estimated_edge_banding_minutes,
            estimated_assembly_minutes=estimated_assembly_minutes,
            estimated_total_factory_minutes=estimated_total_factory_minutes,
            simulation_status=simulation_status,
            simulation_recommendation=simulation_recommendation,
        )

    @staticmethod
    def _is_drilling_operation(operation):
        fields = (
            getattr(operation, "operation_type", ""),
            getattr(operation, "type", ""),
            getattr(operation, "name", ""),
        )
        return any("DRILL" in str(field).upper() for field in fields)
