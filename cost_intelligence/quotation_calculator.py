from cost_intelligence.quotation_report import QuotationReport


class QuotationCalculator:

    def __init__(
        self,
        markup_rate=0.0,
    ):
        self.markup_rate = markup_rate

    def build(
        self,
        cost_report,
    ):
        production_cost = cost_report.total_cost
        markup_amount = production_cost * self.markup_rate
        selling_price = production_cost + markup_amount

        return QuotationReport(
            production_cost=production_cost,
            markup_rate=self.markup_rate,
            markup_amount=markup_amount,
            selling_price=selling_price,
            currency=cost_report.currency,
        )
