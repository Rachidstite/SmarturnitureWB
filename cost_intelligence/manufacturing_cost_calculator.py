from cost_intelligence.manufacturing_cost_report import ManufacturingCostReport
from cost_intelligence.manufacturing_cost_rules_builder import (
    ManufacturingCostRulesBuilder,
)


class ManufacturingCostCalculator:

    def __init__(self, rules=None):
        self.rules = rules or ManufacturingCostRulesBuilder().default()

    def calculate(self, context, *, pricing_catalog=None):
        material_cost = context.total_panel_area_m2 * self.rules.material_area_rate
        edge_banding_cost = self._calculate_edge_banding_cost(
            context,
            pricing_catalog,
        )
        drilling_cost = self._calculate_machining_cost(
            context,
            pricing_catalog,
        )
        complexity_cost = (
            context.total_material_types * self.rules.complexity_material_type_rate
        )
        panel_handling_cost = (
            context.total_panels * self.rules.panel_handling_rate
        )

        return ManufacturingCostReport(
            material_cost=material_cost,
            edge_banding_cost=edge_banding_cost,
            drilling_cost=drilling_cost,
            complexity_cost=complexity_cost,
            panel_handling_cost=panel_handling_cost,
            total_manufacturing_cost=(
                material_cost
                + edge_banding_cost
                + drilling_cost
                + complexity_cost
                + panel_handling_cost
            ),
            currency=self.rules.currency,
            warnings=context.warnings,
        )

    def _calculate_edge_banding_cost(self, context, pricing_catalog):
        if not context.edge_meters_by_banding:
            return context.total_edge_meters * self.rules.edge_meter_rate

        pricing_catalog = pricing_catalog or {}
        total = 0.0
        for banding, meters in context.edge_meters_by_banding.items():
            price_data = pricing_catalog.get(banding) or {}
            price_per_meter = price_data.get(
                "price_per_meter",
                self.rules.edge_meter_rate,
            )
            total += meters * price_per_meter

        return total

    def _calculate_machining_cost(self, context, pricing_catalog):
        if not context.machining_operations_by_type:
            return context.total_drilling_operations * self.rules.drilling_rate

        pricing_catalog = pricing_catalog or {}
        total = 0.0
        for operation_type, operation_count in (
            context.machining_operations_by_type.items()
        ):
            catalog_key = f"MACHINING_{operation_type}"
            price_data = pricing_catalog.get(catalog_key) or {}
            price_per_operation = price_data.get(
                "price_per_operation",
                self.rules.drilling_rate,
            )
            total += operation_count * price_per_operation

        return total
