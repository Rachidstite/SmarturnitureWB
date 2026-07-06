from dataclasses import dataclass


@dataclass
class NestingSavingsReport:
    """Comparison report between two manufacturing cost scenarios.

    Consumes two ManufacturingCostReport instances and computes
    the savings/deltas without any recalculation of cost components.
    All values are positive when the alternative is better (lower cost).
    """

    material_savings: float = 0.0
    waste_reduction: float = 0.0
    recovered_value_delta: float = 0.0
    total_manufacturing_cost_delta: float = 0.0
    profitability_delta: float = 0.0
