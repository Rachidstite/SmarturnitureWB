from manufacturing.manufacturing_metrics_report import ManufacturingMetricsReport


class ManufacturingMetricsBuilder:

    def build(self, production_package):
        cutlist_items = production_package.cutlist_report.items
        edge_items = production_package.edge_report.items
        machining_items = production_package.machining_report.items

        total_panel_area_m2 = sum(
            item["width"] * item["height"] * item["quantity"]
            for item in cutlist_items
        ) / 1_000_000

        total_drilling_operations = sum(
            item["operation_type"] == "DRILL"
            for item in machining_items
        )

        machining_operations_by_type = {}
        for item in machining_items:
            operation_type = item["operation_type"]
            machining_operations_by_type[operation_type] = (
                machining_operations_by_type.get(operation_type, 0)
                + 1
            )

        total_material_types = len(
            {item["material"] for item in cutlist_items}
        )

        edge_meters_by_banding = {}
        for item in edge_items:
            banding = item["banding"]
            edge_meters_by_banding[banding] = (
                edge_meters_by_banding.get(banding, 0.0)
                + item["linear_meters"]
            )

        return ManufacturingMetricsReport(
            total_panels=production_package.summary_report.total_panels,
            total_panel_area_m2=total_panel_area_m2,
            total_edge_meters=(
                production_package.edge_report.total_linear_meters
            ),
            edge_meters_by_banding=edge_meters_by_banding,
            total_drilling_operations=total_drilling_operations,
            machining_operations_by_type=machining_operations_by_type,
            total_material_types=total_material_types,
            warnings_count=len(production_package.warnings),
            warnings=production_package.warnings,
        )
