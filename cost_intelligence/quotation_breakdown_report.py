from dataclasses import dataclass


@dataclass
class QuotationBreakdownReport:
    """
    Commercial-facing quotation cost breakdown.

    This report exposes already-computed cost and price values in a single
    read model for quotation documents, profitability review, and future
    commercial dashboards.

    It does not calculate costs, markup, or selling price.
    """

    material_cost: float = 0.0
    sheet_cost: float = 0.0
    waste_cost: float = 0.0
    hardware_cost: float = 0.0
    edge_banding_cost: float = 0.0
    machining_cost: float = 0.0
    panel_handling_cost: float = 0.0
    manufacturing_cost: float = 0.0
    markup_amount: float = 0.0
    selling_price: float = 0.0
    currency: str = "MAD"
