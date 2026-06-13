from cost_intelligence.cost_estimate import CostEstimate


class HardwareCostCalculator:
    """
    Cost Intelligence V1.

    Calculates furniture hardware cost.
    """

    def estimate(
        self,
        hardware_items=None,
        pricing_catalog=None,
    ):
        hardware_items = hardware_items or []
        pricing_catalog = pricing_catalog or {}

        total = 0
        warnings = []

        for item in hardware_items:
            sku = item.get("sku")
            price_data = pricing_catalog.get(
                sku,
            )

            if price_data is None:
                warnings.append(
                    f"Missing hardware price for {sku}"
                )
                continue

            total += (
                item.get("quantity", 1)
                * price_data.get("unit_price", 0)
            )

        return CostEstimate(
            hardware_cost=total,
            total_cost=total,
            warnings=warnings,
        )
