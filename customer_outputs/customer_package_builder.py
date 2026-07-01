from commercial_outputs.commercial_package_report import CommercialPackageReport

from customer_outputs.customer_package_report import CustomerPackageReport


class CustomerPackageBuilder:
    """Build a passive customer package from a CommercialPackageReport only."""

    def build(self, commercial_report: CommercialPackageReport) -> CustomerPackageReport:
        summary_lines = [
            "Product ready",
            f"Estimated price: {commercial_report.estimated_price}",
        ]
        if commercial_report.warnings:
            summary_lines.append("Commercial warnings:")
            summary_lines.extend(str(warning) for warning in commercial_report.warnings)

        return CustomerPackageReport(
            commercial_report=commercial_report,
            customer_summary="\n".join(summary_lines),
            estimated_price=commercial_report.estimated_price,
            warnings=list(commercial_report.warnings),
            source="CustomerPackageBuilder",
        )
