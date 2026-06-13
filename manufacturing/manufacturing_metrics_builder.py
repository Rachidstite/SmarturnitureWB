from manufacturing.manufacturing_metrics_report import ManufacturingMetricsReport


class ManufacturingMetricsBuilder:

    def build(self, production_package):
        cutlist_items = production_package.cutlist_report.items
        machining_items = production_package.machining_report.items

        total_panel_area_m2 = sum(
            item["width"] * item["height"] * item["quantity"]
            for item in cutlist_items
        ) / 1_000_000

        total_drilling_operations = sum(
            item["operation_type"] == "DRILL"
            for item in machining_items
        )

        total_material_types = len(
            {item["material"] for item in cutlist_items}
        )

        return ManufacturingMetricsReport(
            total_panels=production_package.summary_report.total_panels,
            total_panel_area_m2=total_panel_area_m2,
            total_edge_meters=(
                production_package.edge_report.total_linear_meters
            ),
            total_drilling_operations=total_drilling_operations,
            total_material_types=total_material_types,
            warnings_count=len(production_package.warnings),
            warnings=production_package.warnings,
        )
