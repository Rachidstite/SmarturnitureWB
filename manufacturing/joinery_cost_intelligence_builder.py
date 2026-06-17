from manufacturing.joinery_cost_intelligence_report import (
    JoineryCostIntelligenceReport,
)


class JoineryCostIntelligenceBuilder:

    def __init__(
        self,
        *,
        minifix_unit_cost=0.0,
        hinge_unit_cost=0.0,
        drawer_slide_unit_cost=0.0,
        handle_unit_cost=0.0,
        pricing_catalog=None,
    ):
        self.minifix_unit_cost = minifix_unit_cost
        self.hinge_unit_cost = hinge_unit_cost
        self.drawer_slide_unit_cost = drawer_slide_unit_cost
        self.handle_unit_cost = handle_unit_cost
        self.pricing_catalog = pricing_catalog

    def build(self, joinery_intelligence_report):
        counts = {
            "minifix": int(getattr(joinery_intelligence_report, "total_minifix", 0)),
            "hinge": int(getattr(joinery_intelligence_report, "total_hinges", 0)),
            "drawer_slide": int(getattr(joinery_intelligence_report, "total_drawer_slides", 0)),
            "handle": int(getattr(joinery_intelligence_report, "total_handles", 0)),
        }

        minifix_unit_cost = self._resolve_unit_cost(
            "MINIFIX_15_V1", self.minifix_unit_cost
        )
        hinge_unit_cost = self._resolve_unit_cost(
            "HINGE_BLUM_110_V1", self.hinge_unit_cost
        )
        drawer_slide_unit_cost = self._resolve_unit_cost(
            "DRAWER_SLIDE_SOFTCLOSE_450", self.drawer_slide_unit_cost
        )
        handle_unit_cost = self._resolve_unit_cost(
            "HANDLE_128_BLACK", self.handle_unit_cost
        )

        minifix_cost = counts["minifix"] * minifix_unit_cost
        hinge_cost = counts["hinge"] * hinge_unit_cost
        drawer_slide_cost = counts["drawer_slide"] * drawer_slide_unit_cost
        handle_cost = counts["handle"] * handle_unit_cost

        total_joinery_cost = (
            minifix_cost + hinge_cost + drawer_slide_cost + handle_cost
        )

        cost_breakdown = {
            "minifix": {
                "count": counts["minifix"],
                "unit_cost": minifix_unit_cost,
                "cost": minifix_cost,
            },
            "hinge": {
                "count": counts["hinge"],
                "unit_cost": hinge_unit_cost,
                "cost": hinge_cost,
            },
            "drawer_slide": {
                "count": counts["drawer_slide"],
                "unit_cost": drawer_slide_unit_cost,
                "cost": drawer_slide_cost,
            },
            "handle": {
                "count": counts["handle"],
                "unit_cost": handle_unit_cost,
                "cost": handle_cost,
            },
        }

        warnings = []
        if self.pricing_catalog is None and all(
            value == 0.0
            for value in [
                minifix_unit_cost,
                hinge_unit_cost,
                drawer_slide_unit_cost,
                handle_unit_cost,
            ]
        ):
            warnings.append("Joinery unit costs are defaulting to zero")

        return JoineryCostIntelligenceReport(
            total_joinery_cost=total_joinery_cost,
            minifix_cost=minifix_cost,
            hinge_cost=hinge_cost,
            drawer_slide_cost=drawer_slide_cost,
            handle_cost=handle_cost,
            cost_breakdown=cost_breakdown,
            warnings=warnings,
        )

    def _resolve_unit_cost(self, sku, default_cost):
        item = self._catalog_item(sku)
        if item is None:
            return default_cost
        if hasattr(item, "get"):
            return item.get("unit_price", default_cost)
        return getattr(item, "unit_price", default_cost)

    def _catalog_item(self, sku):
        catalog = self.pricing_catalog
        if catalog is None:
            return None
        if hasattr(catalog, "get"):
            item = catalog.get(sku)
            if item is not None:
                return item
        if isinstance(catalog, dict):
            return catalog.get(sku)
        return getattr(catalog, sku, None)
