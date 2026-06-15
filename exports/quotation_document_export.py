class QuotationDocumentExport:

    @staticmethod
    def render_text(document):
        return "\n".join(
            [
                f"Quotation: {document.quotation_number}",
                f"Issue Date: {document.issue_date}",
                f"Valid Until: {document.valid_until}",
                f"Seller: {document.seller_name}",
                f"Customer: {document.customer_name}",
                f"Project: {document.project_description}",
                f"Total: {document.total_amount} {document.currency}",
                f"Notes: {document.notes}",
                f"Payment Terms: {document.payment_terms}",
            ]
        )
