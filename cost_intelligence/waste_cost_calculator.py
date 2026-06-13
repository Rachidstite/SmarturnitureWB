from cost_intelligence.cost_estimate import CostEstimate


class WasteCostCalculator:
    """
    Cost Intelligence V1.

    Calculates manufacturing waste cost from sheet usage.
    """

    def estimate(
        self,
        nesting_results=None,
        pricing_catalog=None,
    ):
        nesting_results = nesting_results or {}
        pricing_catalog = pricing_catalog or {}

        total = 0
        warnings = []

        for stock_key, sheets in nesting_results.items():
            price_data = pricing_catalog.get(
                stock_key,
            )

            if price_data is None:
                warnings.append(
                    f"Missing sheet price for waste calculation: {stock_key}"
                )
                continue

            price_per_sheet = price_data.get(
                "price_per_sheet",
                0,
            )

            for sheet in sheets:
                waste_ratio = getattr(
                    sheet,
                    "waste_ratio",
                    0,
                )

                total += (
                    price_per_sheet
                    * waste_ratio
                )

        return CostEstimate(
            waste_cost=total,
            total_cost=total,
            warnings=warnings,
        )
