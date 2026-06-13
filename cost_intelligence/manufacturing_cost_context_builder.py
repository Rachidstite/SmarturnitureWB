from cost_intelligence.manufacturing_cost_context import ManufacturingCostContext


class ManufacturingCostContextBuilder:

    def build(self, metrics_report):
        return ManufacturingCostContext(
            total_panels=metrics_report.total_panels,
            total_panel_area_m2=metrics_report.total_panel_area_m2,
            total_edge_meters=metrics_report.total_edge_meters,
            total_drilling_operations=metrics_report.total_drilling_operations,
            total_material_types=metrics_report.total_material_types,
            warnings_count=metrics_report.warnings_count,
            warnings=metrics_report.warnings,
        )
