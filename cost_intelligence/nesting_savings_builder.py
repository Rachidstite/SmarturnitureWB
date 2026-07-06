from cost_intelligence.nesting_savings_report import NestingSavingsReport


def _safe(report, field):
    """Safely read a numeric field from a report, defaulting to 0.0."""
    return float(getattr(report, field, 0.0) or 0.0)


class NestingSavingsBuilder:
    """Computes savings/deltas between two ManufacturingCostReport instances.

    Consumes existing reports only — no recalculation, no cost computation,
    no nesting computation.
    """

    def build(self, current_report, alternative_report):
        material_savings = _safe(current_report, "net_material_cost") - _safe(
            alternative_report, "net_material_cost"
        )
        waste_reduction = _safe(current_report, "waste_cost") - _safe(
            alternative_report, "waste_cost"
        )
        recovered_value_delta = _safe(
            alternative_report, "recovered_value"
        ) - _safe(current_report, "recovered_value")
        total_cost_delta = _safe(
            current_report, "total_manufacturing_cost"
        ) - _safe(alternative_report, "total_manufacturing_cost")

        return NestingSavingsReport(
            material_savings=material_savings,
            waste_reduction=waste_reduction,
            recovered_value_delta=recovered_value_delta,
            total_manufacturing_cost_delta=total_cost_delta,
            profitability_delta=total_cost_delta,
        )
