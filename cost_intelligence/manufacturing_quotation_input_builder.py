from cost_intelligence.manufacturing_quotation_input import (
    ManufacturingQuotationInput,
)


class ManufacturingQuotationInputBuilder:

    def build(
        self,
        manufacturing_cost_summary,
        markup_rate=0.0,
        currency="MAD",
    ):
        return ManufacturingQuotationInput(
            manufacturing_cost_summary=manufacturing_cost_summary,
            base_cost=manufacturing_cost_summary.total_manufacturing_cost,
            markup_rate=markup_rate,
            currency=currency,
            warnings=manufacturing_cost_summary.warnings,
        )
