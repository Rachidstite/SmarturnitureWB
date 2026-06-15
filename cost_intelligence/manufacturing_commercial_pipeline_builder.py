from cost_intelligence.manufacturing_commercial_result import (
    ManufacturingCommercialResult,
)
from cost_intelligence.manufacturing_cost_pipeline_builder import (
    ManufacturingCostPipelineBuilder,
)
from cost_intelligence.manufacturing_profitability_report_builder import (
    ManufacturingProfitabilityReportBuilder,
)
from cost_intelligence.manufacturing_quotation_input_builder import (
    ManufacturingQuotationInputBuilder,
)
from cost_intelligence.manufacturing_quotation_report_builder import (
    ManufacturingQuotationReportBuilder,
)
from cost_intelligence.quotation_intelligence_builder import (
    QuotationIntelligenceBuilder,
)


class ManufacturingCommercialPipelineBuilder:

    def build(
        self,
        manufacturing_production_package,
        markup_rate=0.0,
        currency="MAD",
    ):
        manufacturing_cost_summary = ManufacturingCostPipelineBuilder().build(
            manufacturing_production_package
        )
        manufacturing_quotation_input = (
            ManufacturingQuotationInputBuilder().build(
                manufacturing_cost_summary,
                markup_rate=markup_rate,
                currency=currency,
            )
        )
        quotation_report = ManufacturingQuotationReportBuilder().build(
            manufacturing_quotation_input
        )
        profitability_report = ManufacturingProfitabilityReportBuilder().build(
            quotation_report
        )
        quotation_intelligence_report = QuotationIntelligenceBuilder().build(
            quotation_report,
            profitability_report,
        )
        return ManufacturingCommercialResult(
            manufacturing_cost_summary=manufacturing_cost_summary,
            manufacturing_quotation_input=manufacturing_quotation_input,
            quotation_report=quotation_report,
            profitability_report=profitability_report,
            quotation_intelligence_report=quotation_intelligence_report,
        )
