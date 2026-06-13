import unittest


class TestQuotationValidator(unittest.TestCase):

    def test_quotation_validator_exists(self):

        try:
            from cost_intelligence.quotation_validator import (
                QuotationValidator,
            )
        except ImportError:
            self.fail(
                "QuotationValidator does not exist"
            )

    def test_warns_when_markup_is_negative(self):

        from cost_intelligence.quotation_report import (
            QuotationReport,
        )
        from cost_intelligence.quotation_validator import (
            QuotationValidator,
        )

        report = QuotationReport(
            production_cost=1000,
            markup_rate=-0.10,
            selling_price=900,
            currency="MAD",
        )

        validated = QuotationValidator.validate(report)

        self.assertIn(
            "Negative markup rate",
            validated.warnings,
        )

    def test_warns_when_selling_price_below_production_cost(self):

        from cost_intelligence.quotation_report import (
            QuotationReport,
        )
        from cost_intelligence.quotation_validator import (
            QuotationValidator,
        )

        report = QuotationReport(
            production_cost=1000,
            markup_rate=0,
            selling_price=900,
            currency="MAD",
        )

        validated = QuotationValidator.validate(report)

        self.assertIn(
            "Selling price below production cost",
            validated.warnings,
        )

    def test_accepts_safe_quotation(self):

        from cost_intelligence.quotation_report import (
            QuotationReport,
        )
        from cost_intelligence.quotation_validator import (
            QuotationValidator,
        )

        report = QuotationReport(
            production_cost=1000,
            markup_rate=0.30,
            selling_price=1300,
            currency="MAD",
        )

        validated = QuotationValidator.validate(report)

        self.assertEqual(
            validated.warnings,
            [],
        )


if __name__ == "__main__":
    unittest.main()
