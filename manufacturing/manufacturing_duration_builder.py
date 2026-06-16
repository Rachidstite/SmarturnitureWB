from manufacturing.manufacturing_duration_report import ManufacturingDurationReport


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
        estimated_cnc_minutes = metrics_report.total_panels * 1.0
        estimated_drilling_minutes = (
            metrics_report.total_drilling_operations * 0.5
        )
        estimated_edge_banding_minutes = (
            metrics_report.total_edge_meters * 0.5
        )
        estimated_assembly_minutes = metrics_report.total_panels * 6.0

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
