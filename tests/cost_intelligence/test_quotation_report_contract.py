import unittest
from dataclasses import fields, is_dataclass


class TestQuotationReportContract(unittest.TestCase):

    def test_quotation_report_exists_and_is_dataclass(self):

        try:
            from cost_intelligence.quotation_report import (
                QuotationReport,
            )
        except ImportError:
            self.fail(
                "QuotationReport does not exist"
            )

        self.assertTrue(
            is_dataclass(QuotationReport),
        )

    def test_quotation_report_contains_required_fields(self):

        from cost_intelligence.quotation_report import (
            QuotationReport,
        )

        field_names = {
            field.name
            for field in fields(QuotationReport)
        }

        self.assertEqual(
            field_names,
            {
                "production_cost",
                "markup_rate",
                "markup_amount",
                "discount_amount",
                "tax_amount",
                "selling_price",
                "currency",
                "warnings",
            },
        )

    def test_quotation_report_has_safe_defaults(self):

        from cost_intelligence.quotation_report import (
            QuotationReport,
        )

        report = QuotationReport()

        self.assertEqual(report.production_cost, 0.0)
        self.assertEqual(report.markup_rate, 0.0)
        self.assertEqual(report.markup_amount, 0.0)
        self.assertEqual(report.discount_amount, 0.0)
        self.assertEqual(report.tax_amount, 0.0)
        self.assertEqual(report.selling_price, 0.0)
        self.assertEqual(report.currency, "MAD")
        self.assertEqual(report.warnings, [])


if __name__ == "__main__":
    unittest.main()
