from commercial_outputs.commercial_package_report import CommercialPackageReport
from cost_intelligence.cost_package_report import CostPackageReport


class CommercialPackageBuilder:
    """Build a ``CommercialPackageReport`` from a ``CostPackageReport``.

    This layer performs **no** pricing-policy calculation, quotation
    formatting, tax, discount, or currency logic.  When no pricing
    policy is configured (the default at this layer), estimated price
    equals cost and margin is zero — this is a deliberate signal that
    a downstream policy engine is needed.
    """

    NO_PRICING_POLICY = "No commercial pricing policy configured."

    def build(self, cost_report: CostPackageReport) -> CommercialPackageReport:
        """Return a ``CommercialPackageReport`` derived from *cost_report*."""
        return CommercialPackageReport(
            cost_report=cost_report,
            estimated_price=cost_report.total_cost,
            margin_amount=0.0,
            margin_percent=0.0,
            warnings=[self.NO_PRICING_POLICY],
            source="CommercialPackageBuilder",
        )
