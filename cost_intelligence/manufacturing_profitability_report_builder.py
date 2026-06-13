from cost_intelligence.profitability_calculator import ProfitabilityCalculator


class ManufacturingProfitabilityReportBuilder:

    def build(self, quotation_report):
        return ProfitabilityCalculator().build(quotation_report)
