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
    @staticmethod
    def render_breakdown_text(document, breakdown):
        """
        Render an internal quotation breakdown.

        This output is intended for seller-side review and profitability
        analysis. It is separate from render_text(document), which remains the
        customer-facing quotation output.
        """

        currency = breakdown.currency or document.currency

        return "\n".join(
            [
                f"Quotation: {document.quotation_number}",
                f"Issue Date: {document.issue_date}",
                f"Valid Until: {document.valid_until}",
                f"Seller: {document.seller_name}",
                f"Customer: {document.customer_name}",
                f"Project: {document.project_description}",
                f"Material Cost: {breakdown.material_cost} {currency}",
                f"Sheet Cost: {breakdown.sheet_cost} {currency}",
                f"Waste Cost: {breakdown.waste_cost} {currency}",
                f"Hardware Cost: {breakdown.hardware_cost} {currency}",
                f"Edge Banding Cost: {breakdown.edge_banding_cost} {currency}",
                f"Machining Cost: {breakdown.machining_cost} {currency}",
                f"Panel Handling Cost: {breakdown.panel_handling_cost} {currency}",
                f"Manufacturing Cost: {breakdown.manufacturing_cost} {currency}",
                f"Markup Amount: {breakdown.markup_amount} {currency}",
                f"Selling Price: {breakdown.selling_price} {currency}",
                f"Notes: {document.notes}",
                f"Payment Terms: {document.payment_terms}",
            ]
        )
