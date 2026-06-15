import unittest
from dataclasses import fields, is_dataclass


class TestQuotationIntelligenceReportContract(unittest.TestCase):

    def test_report_is_dataclass(self):
        from cost_intelligence.quotation_intelligence_report import (
            QuotationIntelligenceReport,
        )

        self.assertTrue(is_dataclass(QuotationIntelligenceReport))

    def test_report_has_exact_field_order(self):
        from cost_intelligence.quotation_intelligence_report import (
            QuotationIntelligenceReport,
        )

        self.assertEqual(
            [field.name for field in fields(QuotationIntelligenceReport)],
            [
                "risk_level",
                "margin_status",
                "recommendations",
            ],
        )

    def test_report_has_safe_defaults(self):
        from cost_intelligence.quotation_intelligence_report import (
            QuotationIntelligenceReport,
        )

        report = QuotationIntelligenceReport()

        self.assertEqual(report.risk_level, "UNKNOWN")
        self.assertEqual(report.margin_status, "UNKNOWN")
        self.assertEqual(report.recommendations, [])


if __name__ == "__main__":
    unittest.main()
