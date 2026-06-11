from cost_intelligence.cost_estimate import CostEstimate


class SheetCostCalculator:
    """
    Cost Intelligence V1.

    Calculates purchased sheet cost from nesting results.
    """

    def estimate(
        self,
        nesting_results=None,
        pricing_catalog=None,
    ):
        nesting_results = nesting_results or {}
        pricing_catalog = pricing_catalog or {}

        total = 0

        for stock_key, sheets in nesting_results.items():
            price_data = pricing_catalog.get(
                stock_key,
                {},
            )

            price_per_sheet = price_data.get(
                "price_per_sheet",
                0,
            )

            total += (
                len(sheets)
                * price_per_sheet
            )

        return CostEstimate(
            sheet_cost=total,
            total_cost=total,
        )
