from cost_intelligence.furniture_project_quotation_breakdown_builder import (
    FurnitureProjectQuotationBreakdownBuilder,
)


class FurnitureProjectProfitabilityBuilder:

    def build(self, furniture_project, markup_rate=0.0, currency="MAD"):
        breakdowns = FurnitureProjectQuotationBreakdownBuilder().build(
            furniture_project,
            markup_rate=markup_rate,
            currency=currency,
        )
        return self._build_report(
            breakdowns=breakdowns,
            currency=currency,
        )

    def _build_report(self, breakdowns, currency="MAD"):
        total_manufacturing_cost = sum(
            item["total_manufacturing_cost"]
            for item in breakdowns
        )
        total_selling_price = sum(
            item["selling_price"]
            for item in breakdowns
        )
        gross_profit = total_selling_price - total_manufacturing_cost

        if total_selling_price > 0:
            gross_margin_rate = gross_profit / total_selling_price
        else:
            gross_margin_rate = 0.0

        return {
            "total_manufacturing_cost": total_manufacturing_cost,
            "total_selling_price": total_selling_price,
            "gross_profit": gross_profit,
            "gross_margin_rate": gross_margin_rate,
            "currency": currency,
        }
