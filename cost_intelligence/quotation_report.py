from dataclasses import dataclass, field


@dataclass
class QuotationReport:
    """
    Customer-facing quotation contract.
    """

    production_cost: float = 0.0

    markup_rate: float = 0.0

    markup_amount: float = 0.0

    discount_amount: float = 0.0

    tax_amount: float = 0.0

    selling_price: float = 0.0

    currency: str = "MAD"

    warnings: list = field(
        default_factory=list
    )
