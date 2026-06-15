from cost_intelligence.furniture_project_business_report import (
    FurnitureProjectBusinessReport,
)
from cost_intelligence.furniture_project_factory_decision_builder import (
    FurnitureProjectFactoryDecisionBuilder,
)
from cost_intelligence.furniture_project_profitability_builder import (
    FurnitureProjectProfitabilityBuilder,
)
from cost_intelligence.furniture_project_quotation_breakdown_builder import (
    FurnitureProjectQuotationBreakdownBuilder,
)
from cost_intelligence.furniture_project_quotation_builder import (
    FurnitureProjectQuotationBuilder,
)
from manufacturing.furniture_project_summary_builder import (
    FurnitureProjectSummaryBuilder,
)


class FurnitureProjectBusinessReportBuilder:

    def build(
        self,
        furniture_project,
        *,
        quotation_number,
        issue_date,
        valid_until,
        seller_name,
        customer_name,
        project_description,
        markup_rate=0.0,
        currency="MAD",
        notes="",
        payment_terms="",
    ):
        project_summary = FurnitureProjectSummaryBuilder().build(
            furniture_project
        )
        quotation_document = FurnitureProjectQuotationBuilder().build(
            furniture_project,
            quotation_number=quotation_number,
            issue_date=issue_date,
            valid_until=valid_until,
            seller_name=seller_name,
            customer_name=customer_name,
            project_description=project_description,
            markup_rate=markup_rate,
            currency=currency,
            notes=notes,
            payment_terms=payment_terms,
        )
        quotation_breakdowns = FurnitureProjectQuotationBreakdownBuilder().build(
            furniture_project,
            markup_rate=markup_rate,
            currency=currency,
        )
        profitability_report = FurnitureProjectProfitabilityBuilder().build(
            furniture_project,
            markup_rate=markup_rate,
            currency=currency,
        )
        factory_decision_report = FurnitureProjectFactoryDecisionBuilder().build(
            furniture_project,
            markup_rate=markup_rate,
            currency=currency,
        )

        return FurnitureProjectBusinessReport(
            project_summary=project_summary,
            quotation_document=quotation_document,
            quotation_breakdowns=quotation_breakdowns,
            profitability_report=profitability_report,
            executive_report=None,
            factory_decision_report=factory_decision_report,
        )
