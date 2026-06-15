import unittest


class TestQuotationIntelligenceBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.quotation_intelligence_builder import (
            QuotationIntelligenceBuilder,
        )

        self.assertTrue(callable(QuotationIntelligenceBuilder().build))

    def test_build_returns_high_risk_below_fifteen_percent(self):
        report = self._build(gross_margin_rate=0.149)

        self.assertEqual(report.risk_level, "HIGH")
        self.assertEqual(report.margin_status, "LOW_MARGIN")
        self.assertIn("Increase selling price.", report.recommendations)

    def test_build_returns_medium_risk_at_fifteen_percent(self):
        report = self._build(gross_margin_rate=0.15)

        self.assertEqual(report.risk_level, "MEDIUM")
        self.assertEqual(report.margin_status, "ACCEPTABLE_MARGIN")
        self.assertIn("Review quote before approval.", report.recommendations)

    def test_build_returns_medium_risk_below_twenty_five_percent(self):
        report = self._build(gross_margin_rate=0.249)

        self.assertEqual(report.risk_level, "MEDIUM")
        self.assertEqual(report.margin_status, "ACCEPTABLE_MARGIN")
        self.assertIn("Review quote before approval.", report.recommendations)

    def test_build_returns_low_risk_at_twenty_five_percent(self):
        report = self._build(gross_margin_rate=0.25)

        self.assertEqual(report.risk_level, "LOW")
        self.assertEqual(report.margin_status, "HEALTHY_MARGIN")
        self.assertIn("Healthy quotation.", report.recommendations)

    def test_build_returns_low_risk_above_twenty_five_percent(self):
        report = self._build(gross_margin_rate=0.40)

        self.assertEqual(report.risk_level, "LOW")
        self.assertEqual(report.margin_status, "HEALTHY_MARGIN")
        self.assertIn("Healthy quotation.", report.recommendations)

    def test_build_populates_recommendations(self):
        report = self._build(gross_margin_rate=0.20)

        self.assertEqual(report.recommendations, ["Review quote before approval."])

    def test_builder_does_not_mutate_quotation_report(self):
        from cost_intelligence.profitability_report import ProfitabilityReport
        from cost_intelligence.quotation_intelligence_builder import (
            QuotationIntelligenceBuilder,
        )
        from cost_intelligence.quotation_report import QuotationReport

        quotation_report = QuotationReport(
            production_cost=1000.0,
            selling_price=1250.0,
            warnings=["Quotation warning"],
        )
        profitability_report = ProfitabilityReport(gross_margin_rate=0.20)
        original_values = quotation_report.__dict__.copy()

        QuotationIntelligenceBuilder().build(
            quotation_report,
            profitability_report,
        )

        self.assertEqual(quotation_report.__dict__, original_values)

    def test_builder_does_not_mutate_profitability_report(self):
        from cost_intelligence.profitability_report import ProfitabilityReport
        from cost_intelligence.quotation_intelligence_builder import (
            QuotationIntelligenceBuilder,
        )
        from cost_intelligence.quotation_report import QuotationReport

        quotation_report = QuotationReport()
        profitability_report = ProfitabilityReport(
            gross_margin_rate=0.20,
            warnings=["Profitability warning"],
        )
        original_values = profitability_report.__dict__.copy()

        QuotationIntelligenceBuilder().build(
            quotation_report,
            profitability_report,
        )

        self.assertEqual(profitability_report.__dict__, original_values)

    @staticmethod
    def _build(gross_margin_rate):
        from cost_intelligence.profitability_report import ProfitabilityReport
        from cost_intelligence.quotation_intelligence_builder import (
            QuotationIntelligenceBuilder,
        )
        from cost_intelligence.quotation_report import QuotationReport

        return QuotationIntelligenceBuilder().build(
            QuotationReport(),
            ProfitabilityReport(gross_margin_rate=gross_margin_rate),
        )


if __name__ == "__main__":
    unittest.main()
