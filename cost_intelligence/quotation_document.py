from dataclasses import dataclass


@dataclass
class QuotationDocumentV1:
    quotation_number: str = ""
    issue_date: str = ""
    valid_until: str = ""
    seller_name: str = ""
    customer_name: str = ""
    project_description: str = ""
    total_amount: float = 0.0
    currency: str = "MAD"
    notes: str = ""
    payment_terms: str = ""
