import unittest
from unittest.mock import patch


class TestManufacturingQuotationReportBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.manufacturing_quotation_report_builder import (
            ManufacturingQuotationReportBuilder,
        )

        self.assertTrue(callable(ManufacturingQuotationReportBuilder().build))

    def test_build_maps_input_to_quotation_report(self):
        from cost_intelligence.manufacturing_quotation_input import (
            ManufacturingQuotationInput,
        )
        from cost_intelligence.manufacturing_quotation_report_builder import (
            ManufacturingQuotationReportBuilder,
        )
        from cost_intelligence.quotation_report import QuotationReport

        warnings = ["Manufacturing warning"]
        quotation_input = ManufacturingQuotationInput(
            base_cost=1000.0,
            markup_rate=0.25,
            currency="EUR",
            warnings=warnings,
        )

        report = ManufacturingQuotationReportBuilder().build(quotation_input)

        self.assertIsInstance(report, QuotationReport)
        self.assertEqual(report.production_cost, 1000.0)
        self.assertEqual(report.markup_rate, 0.25)
        self.assertEqual(report.markup_amount, 250.0)
        self.assertEqual(report.selling_price, 1250.0)
        self.assertEqual(report.currency, "EUR")
        self.assertIs(report.warnings, warnings)

    def test_build_reuses_quotation_calculator(self):
        from cost_intelligence.manufacturing_quotation_input import (
            ManufacturingQuotationInput,
        )
        from cost_intelligence.manufacturing_quotation_report_builder import (
            ManufacturingQuotationReportBuilder,
        )
        from cost_intelligence.quotation_report import QuotationReport

        expected_report = QuotationReport()

        with patch(
            "cost_intelligence.manufacturing_quotation_report_builder."
            "QuotationCalculator"
        ) as calculator_class:
            calculator_class.return_value.build.return_value = expected_report

            report = ManufacturingQuotationReportBuilder().build(
                ManufacturingQuotationInput(markup_rate=0.2)
            )

        calculator_class.assert_called_once_with(markup_rate=0.2)
        calculator_class.return_value.build.assert_called_once()
        self.assertIs(report, expected_report)


if __name__ == "__main__":
    unittest.main()
