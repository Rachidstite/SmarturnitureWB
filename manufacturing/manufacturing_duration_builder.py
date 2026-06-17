from manufacturing.manufacturing_duration_report import ManufacturingDurationReport
from manufacturing.factory_time_catalog_service import (
    FactoryTimeCatalogService,
)


class ManufacturingDurationBuilder:
    """
    Estimates production duration from manufacturing metrics.

    Rates are intentionally simple V1 assumptions:
    - CNC: 1 minute per panel
    - Drilling: 0.5 minute per drilling operation
    - Edge banding: 0.5 minute per linear meter
    - Assembly: 6 minutes per panel
    """

    def build(self, metrics_report):
        catalog = FactoryTimeCatalogService().load()
        cnc_minutes_per_panel = catalog.get("cnc_minutes_per_panel", 1.0)
        drill_minutes_per_operation = catalog.get(
            "drill_minutes_per_operation",
            0.5,
        )
        edge_banding_minutes_per_meter = catalog.get(
            "edge_banding_minutes_per_meter",
            0.5,
        )
        assembly_minutes_per_panel = catalog.get(
            "assembly_minutes_per_panel",
            6.0,
        )

        estimated_cnc_minutes = (
            metrics_report.total_panels * cnc_minutes_per_panel
        )
        estimated_drilling_minutes = (
            metrics_report.total_drilling_operations
            * drill_minutes_per_operation
        )
        estimated_edge_banding_minutes = (
            metrics_report.total_edge_meters * edge_banding_minutes_per_meter
        )
        estimated_assembly_minutes = (
            metrics_report.total_panels * assembly_minutes_per_panel
        )

        total_production_minutes = (
            estimated_cnc_minutes
            + estimated_drilling_minutes
            + estimated_edge_banding_minutes
            + estimated_assembly_minutes
        )

        return ManufacturingDurationReport(
            estimated_cnc_minutes=estimated_cnc_minutes,
            estimated_drilling_minutes=estimated_drilling_minutes,
            estimated_edge_banding_minutes=estimated_edge_banding_minutes,
            estimated_assembly_minutes=estimated_assembly_minutes,
            total_production_minutes=total_production_minutes,
            warnings=list(metrics_report.warnings),
        )
