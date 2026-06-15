from cost_intelligence.quotation_document import QuotationDocumentV1


class QuotationDocumentBuilderV1:

    def build(
        self,
        quotation_report,
        *,
        quotation_number,
        issue_date,
        valid_until,
        seller_name,
        customer_name,
        project_description,
        notes="",
        payment_terms="",
    ):
        return QuotationDocumentV1(
            quotation_number=quotation_number,
            issue_date=issue_date,
            valid_until=valid_until,
            seller_name=seller_name,
            customer_name=customer_name,
            project_description=project_description,
            total_amount=quotation_report.selling_price,
            currency=quotation_report.currency,
            notes=notes,
            payment_terms=payment_terms,
        )
