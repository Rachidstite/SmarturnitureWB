from cost_intelligence.cost_report import CostReport
from cost_intelligence.quotation_calculator import QuotationCalculator


class ManufacturingQuotationReportBuilder:

    def build(self, manufacturing_quotation_input):
        cost_report = CostReport(
            total_cost=manufacturing_quotation_input.base_cost,
            currency=manufacturing_quotation_input.currency,
        )
        quotation_report = QuotationCalculator(
            markup_rate=manufacturing_quotation_input.markup_rate,
        ).build(cost_report)
        quotation_report.warnings = manufacturing_quotation_input.warnings
        return quotation_report
