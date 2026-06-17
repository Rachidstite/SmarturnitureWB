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
        self.assertEqual(
            profitability.profitability_status,
            "HIGH",
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
        self.assertEqual(
            profitability.profitability_status,
            "LOW",
        )

    def test_builds_profitability_status_for_margin_bands(self):

        from cost_intelligence.profitability_calculator import (
            ProfitabilityCalculator,
        )
        from cost_intelligence.quotation_report import (
            QuotationReport,
        )

        low = ProfitabilityCalculator().build(
            QuotationReport(
                production_cost=950,
                selling_price=1000,
                currency="MAD",
            )
        )
        medium = ProfitabilityCalculator().build(
            QuotationReport(
                production_cost=850,
                selling_price=1000,
                currency="MAD",
            )
        )
        high = ProfitabilityCalculator().build(
            QuotationReport(
                production_cost=700,
                selling_price=1000,
                currency="MAD",
            )
        )

        self.assertEqual(low.profitability_status, "LOW")
        self.assertEqual(medium.profitability_status, "MEDIUM")
        self.assertEqual(high.profitability_status, "HIGH")


if __name__ == "__main__":
    unittest.main()
