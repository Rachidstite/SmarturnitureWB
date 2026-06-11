from cost_intelligence.cost_estimate import CostEstimate


class MaterialCostCalculator:
    """
    Minimal Cost Intelligence V1 component.

    Calculates material cost from CutListItem area and pricing catalog.
    """

    def estimate(
        self,
        cutlist_items=None,
        pricing_catalog=None,
    ):
        cutlist_items = cutlist_items or []
        pricing_catalog = pricing_catalog or {}

        total = 0

        for item in cutlist_items:
            thickness = getattr(
                item,
                "thickness",
                0,
            )

            thickness_label = f"{thickness:g}MM"
            material = str(
                getattr(
                    item,
                    "material",
                    "",
                )
            )

            if material.upper().endswith(
                f"_{thickness_label}".upper()
            ):
                stock_key = material
            else:
                stock_key = (
                    f"{material}_{thickness_label}"
                )

            price_data = pricing_catalog.get(
                stock_key,
                {},
            )

            price_per_m2 = price_data.get(
                "price_per_m2",
                0,
            )

            area_m2 = (
                getattr(item, "width", 0)
                * getattr(item, "height", 0)
                / 1_000_000
            )

            quantity = getattr(
                item,
                "quantity",
                1,
            )

            total += (
                area_m2
                * price_per_m2
                * quantity
            )

        return CostEstimate(
            material_cost=total,
            total_cost=total,
        )
