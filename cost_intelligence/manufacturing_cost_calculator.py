from cost_intelligence.manufacturing_cost_report import ManufacturingCostReport
from cost_intelligence.manufacturing_cost_rules_builder import (
    ManufacturingCostRulesBuilder,
)


def _get_labor_field(report, field_name: str) -> float:
    """Safely read a numeric field from an optional labor cost report."""
    if report is None:
        return 0.0
    return float(getattr(report, field_name, 0.0) or 0.0)


class ManufacturingCostCalculator:

    def __init__(self, rules=None):
        self.rules = rules or ManufacturingCostRulesBuilder().default()

    def calculate(self, context, *, pricing_catalog=None, hardware_cost=0.0,
                  labor_cost_report=None):
        hardware_cost = hardware_cost or 0.0
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

        # Labor costs from optional labor_cost_report (backward compatible)
        cnc_labor_cost = _get_labor_field(labor_cost_report, "cnc_labor_cost")
        drilling_labor_cost = _get_labor_field(labor_cost_report, "drilling_labor_cost")
        edge_banding_labor_cost = _get_labor_field(labor_cost_report, "edge_banding_labor_cost")
        assembly_labor_cost = _get_labor_field(labor_cost_report, "assembly_labor_cost")
        total_labor_cost = _get_labor_field(labor_cost_report, "total_labor_cost")

        labor_warnings = list(
            getattr(labor_cost_report, "warnings", []) if labor_cost_report is not None else []
        )
        combined_warnings = context.warnings + labor_warnings

        base_cost_before_overhead = (
            material_cost
            + edge_banding_cost
            + drilling_cost
            + hardware_cost
            + complexity_cost
            + panel_handling_cost
            + total_labor_cost
        )

        overhead_cost = (
            self.rules.overhead_flat_cost
            + (base_cost_before_overhead * self.rules.overhead_percentage)
        )

        return ManufacturingCostReport(
            material_cost=material_cost,
            edge_banding_cost=edge_banding_cost,
            drilling_cost=drilling_cost,
            hardware_cost=hardware_cost,
            complexity_cost=complexity_cost,
            panel_handling_cost=panel_handling_cost,
            cnc_labor_cost=cnc_labor_cost,
            drilling_labor_cost=drilling_labor_cost,
            edge_banding_labor_cost=edge_banding_labor_cost,
            assembly_labor_cost=assembly_labor_cost,
            total_labor_cost=total_labor_cost,
            overhead_cost=overhead_cost,
            total_manufacturing_cost=(
                base_cost_before_overhead + overhead_cost
            ),
            currency=self.rules.currency,
            warnings=combined_warnings,
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
                self.rules.operation_rates.get(
                    operation_type, self.rules.drilling_rate
                ),
            )
            total += operation_count * price_per_operation

        return total
