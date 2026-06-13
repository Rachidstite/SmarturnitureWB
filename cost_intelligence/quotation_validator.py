from cost_intelligence.quotation_report import QuotationReport


class QuotationValidator:

    @staticmethod
    def validate(
        report,
    ):
        warnings = list(report.warnings)

        if report.markup_rate < 0:
            warnings.append(
                "Negative markup rate"
            )

        if report.selling_price < report.production_cost:
            warnings.append(
                "Selling price below production cost"
            )

        return QuotationReport(
            production_cost=report.production_cost,
            markup_rate=report.markup_rate,
            markup_amount=report.markup_amount,
            discount_amount=report.discount_amount,
            tax_amount=report.tax_amount,
            selling_price=report.selling_price,
            currency=report.currency,
            warnings=warnings,
        )
