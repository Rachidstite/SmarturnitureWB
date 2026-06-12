import unittest


class TestProfitabilityCalculator(unittest.TestCase):

    def test_profitability_calculator_exists(self):

        try:
            from cost_intelligence.profitability_calculator import (
                ProfitabilityCalculator,
            )
        except ImportError:
            self.fail(
                "ProfitabilityCalculator does not exist"
            )

    def test_builds_profitability_from_quotation_report(self):

        from cost_intelligence.profitability_calculator import (
            ProfitabilityCalculator,
        )
        from cost_intelligence.quotation_report import (
            QuotationReport,
        )

        report = QuotationReport(
            production_cost=1000,
            selling_price=1300,
            currency="MAD",
        )

        profitability = ProfitabilityCalculator().build(report)

        self.assertEqual(
            profitability.production_cost,
            1000,
        )
        self.assertEqual(
            profitability.selling_price,
            1300,
        )
        self.assertEqual(
            profitability.gross_profit,
            300,
        )
        self.assertEqual(
            profitability.gross_margin_rate,
            300 / 1300,
        )

    def test_handles_zero_selling_price_safely(self):

        from cost_intelligence.profitability_calculator import (
            ProfitabilityCalculator,
        )
        from cost_intelligence.quotation_report import (
            QuotationReport,
        )

        report = QuotationReport(
            production_cost=1000,
            selling_price=0,
            currency="MAD",
        )

        profitability = ProfitabilityCalculator().build(report)

        self.assertEqual(
            profitability.gross_profit,
            -1000,
        )
        self.assertEqual(
            profitability.gross_margin_rate,
            0,
        )


if __name__ == "__main__":
    unittest.main()
