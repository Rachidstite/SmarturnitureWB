from dataclasses import dataclass, field


@dataclass
class CustomerPackageReport:
    """Passive customer-facing summary built from a CommercialPackageReport."""

    commercial_report: object = None
    customer_summary: str = ""
    estimated_price: float = 0.0
    warnings: list = field(default_factory=list)
    source: str = ""
