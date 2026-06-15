from cost_intelligence.manufacturing_commercial_pipeline_builder import (
    ManufacturingCommercialPipelineBuilder,
)
from cost_intelligence.quotation_document_builder import (
    QuotationDocumentBuilderV1,
)
from manufacturing.furniture_project_manufacturing_package_builder import (
    FurnitureProjectManufacturingPackageBuilder,
)
from manufacturing.manufacturing_production_package_builder import (
    ManufacturingProductionPackageBuilder,
)


class FurnitureProjectQuotationBuilder:

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
        manufacturing_package = (
            FurnitureProjectManufacturingPackageBuilder().build(
                furniture_project
            )
        )
        manufacturing_production_package = (
            ManufacturingProductionPackageBuilder().build(
                manufacturing_package
            )
        )
        commercial_result = ManufacturingCommercialPipelineBuilder().build(
            manufacturing_production_package,
            markup_rate,
            currency,
        )
        return QuotationDocumentBuilderV1().build(
            commercial_result.quotation_report,
            quotation_number=quotation_number,
            issue_date=issue_date,
            valid_until=valid_until,
            seller_name=seller_name,
            customer_name=customer_name,
            project_description=project_description,
            notes=notes,
            payment_terms=payment_terms,
        )
