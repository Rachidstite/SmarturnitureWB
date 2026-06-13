import unittest
from unittest.mock import patch


class TestManufacturingProfitabilityReportBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.manufacturing_profitability_report_builder import (
            ManufacturingProfitabilityReportBuilder,
        )

        self.assertTrue(callable(ManufacturingProfitabilityReportBuilder().build))

    def test_build_returns_profitability_report(self):
        from cost_intelligence.manufacturing_profitability_report_builder import (
            ManufacturingProfitabilityReportBuilder,
        )
        from cost_intelligence.profitability_report import ProfitabilityReport
        from cost_intelligence.quotation_report import QuotationReport

        warnings = ["Quotation warning"]
        quotation_report = QuotationReport(
            production_cost=1000.0,
            selling_price=1250.0,
            currency="EUR",
            warnings=warnings,
        )

        report = ManufacturingProfitabilityReportBuilder().build(
            quotation_report
        )

        self.assertIsInstance(report, ProfitabilityReport)
        self.assertEqual(report.production_cost, 1000.0)
        self.assertEqual(report.selling_price, 1250.0)
        self.assertEqual(report.gross_profit, 250.0)
        self.assertEqual(report.gross_margin_rate, 250.0 / 1250.0)
        self.assertEqual(report.currency, "EUR")
        self.assertEqual(report.warnings, warnings)

    def test_build_reuses_profitability_calculator(self):
        from cost_intelligence.manufacturing_profitability_report_builder import (
            ManufacturingProfitabilityReportBuilder,
        )
        from cost_intelligence.profitability_report import ProfitabilityReport
        from cost_intelligence.quotation_report import QuotationReport

        quotation_report = QuotationReport()
        expected_report = ProfitabilityReport()

        with patch(
            "cost_intelligence.manufacturing_profitability_report_builder."
            "ProfitabilityCalculator"
        ) as calculator_class:
            calculator_class.return_value.build.return_value = expected_report

            report = ManufacturingProfitabilityReportBuilder().build(
                quotation_report
            )

        calculator_class.assert_called_once_with()
        calculator_class.return_value.build.assert_called_once_with(
            quotation_report
        )
        self.assertIs(report, expected_report)


if __name__ == "__main__":
    unittest.main()
