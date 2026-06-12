from cost_intelligence.profitability_report import ProfitabilityReport


class ProfitabilityCalculator:

    def build(
        self,
        quotation_report,
    ):
        production_cost = quotation_report.production_cost
        selling_price = quotation_report.selling_price
        gross_profit = selling_price - production_cost

        if selling_price > 0:
            gross_margin_rate = gross_profit / selling_price
        else:
            gross_margin_rate = 0

        return ProfitabilityReport(
            production_cost=production_cost,
            selling_price=selling_price,
            gross_profit=gross_profit,
            gross_margin_rate=gross_margin_rate,
            currency=quotation_report.currency,
            warnings=list(quotation_report.warnings),
        )
