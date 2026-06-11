from cost_intelligence.cost_estimate import CostEstimate


class CostSummaryCalculator:
    """
    Cost Intelligence V1.

    Aggregates cost estimates into one production cost summary.
    """

    def estimate(
        self,
        material_estimate=None,
        sheet_estimate=None,
        waste_estimate=None,
    ):
        material_estimate = material_estimate or CostEstimate()
        sheet_estimate = sheet_estimate or CostEstimate()
        waste_estimate = waste_estimate or CostEstimate()

        material_cost = material_estimate.material_cost
        sheet_cost = sheet_estimate.sheet_cost
        waste_cost = waste_estimate.waste_cost

        return CostEstimate(
            material_cost=material_cost,
            sheet_cost=sheet_cost,
            waste_cost=waste_cost,
            total_cost=(
                material_cost
                + sheet_cost
                + waste_cost
            ),
            warnings=(
                material_estimate.warnings
                + sheet_estimate.warnings
                + waste_estimate.warnings
            ),
        )
