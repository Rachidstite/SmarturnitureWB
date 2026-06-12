from cost_intelligence.manufacturing_cost_report import ManufacturingCostReport


class ManufacturingCostCalculator:

    def calculate(self, context):
        material_cost = context.total_panel_area_m2 * 120.0
        edge_banding_cost = context.total_edge_meters * 5.0
        drilling_cost = context.total_drilling_operations * 1.5
        complexity_cost = context.total_material_types * 25.0

        return ManufacturingCostReport(
            material_cost=material_cost,
            edge_banding_cost=edge_banding_cost,
            drilling_cost=drilling_cost,
            complexity_cost=complexity_cost,
            total_manufacturing_cost=(
                material_cost
                + edge_banding_cost
                + drilling_cost
                + complexity_cost
            ),
            currency="MAD",
            warnings=context.warnings,
        )
