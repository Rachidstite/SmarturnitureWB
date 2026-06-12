import unittest


class TestQuotationCalculator(unittest.TestCase):

    def test_quotation_calculator_exists(self):

        try:
            from cost_intelligence.quotation_calculator import (
                QuotationCalculator,
            )
        except ImportError:
            self.fail(
                "QuotationCalculator does not exist"
            )

    def test_builds_quotation_from_cost_report(self):

        from cost_intelligence.cost_report import CostReport
        from cost_intelligence.quotation_calculator import (
            QuotationCalculator,
        )

        report = CostReport(
            total_cost=1000.0,
            currency="MAD",
        )

        quotation = QuotationCalculator(
            markup_rate=0.30,
        ).build(report)

        self.assertEqual(
            quotation.production_cost,
            1000.0,
        )
        self.assertEqual(
            quotation.markup_amount,
            300.0,
        )
        self.assertEqual(
            quotation.selling_price,
            1300.0,
        )
        self.assertEqual(
            quotation.currency,
            "MAD",
        )

    def test_zero_markup_keeps_same_price(self):

        from cost_intelligence.cost_report import CostReport
        from cost_intelligence.quotation_calculator import (
            QuotationCalculator,
        )

        report = CostReport(
            total_cost=1000,
            currency="MAD",
        )

        quotation = QuotationCalculator(
            markup_rate=0,
        ).build(report)

        self.assertEqual(
            quotation.selling_price,
            1000,
        )


if __name__ == "__main__":
    unittest.main()
