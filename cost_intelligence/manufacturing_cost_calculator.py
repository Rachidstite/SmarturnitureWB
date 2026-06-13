from cost_intelligence.manufacturing_cost_report import ManufacturingCostReport
from cost_intelligence.manufacturing_cost_rules_builder import (
    ManufacturingCostRulesBuilder,
)


class ManufacturingCostCalculator:

    def __init__(self, rules=None):
        self.rules = rules or ManufacturingCostRulesBuilder().default()

    def calculate(self, context):
        material_cost = context.total_panel_area_m2 * self.rules.material_area_rate
        edge_banding_cost = context.total_edge_meters * self.rules.edge_meter_rate
        drilling_cost = context.total_drilling_operations * self.rules.drilling_rate
        complexity_cost = (
            context.total_material_types * self.rules.complexity_material_type_rate
        )

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
            currency=self.rules.currency,
            warnings=context.warnings,
        )
