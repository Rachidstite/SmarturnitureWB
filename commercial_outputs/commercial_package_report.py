from dataclasses import dataclass, field


@dataclass
class CommercialPackageReport:
    """Passive commercial summary built from a ``CostPackageReport``.

    No pricing policy, no quotation formatting, no tax, no discounts,
    no currencies, no payment terms — this is the neutral foundation
    that a downstream policy engine would enrich.
    """

    cost_report: object = None
    estimated_price: float = 0.0
    margin_amount: float = 0.0
    margin_percent: float = 0.0
    warnings: list = field(default_factory=list)
    source: str = ""
