import unittest
from dataclasses import fields, is_dataclass


class TestProfitabilityReportContract(unittest.TestCase):

    def test_profitability_report_exists_and_is_dataclass(self):

        try:
            from cost_intelligence.profitability_report import (
                ProfitabilityReport,
            )
        except ImportError:
            self.fail(
                "ProfitabilityReport does not exist"
            )

        self.assertTrue(
            is_dataclass(ProfitabilityReport),
        )

    def test_profitability_report_contains_required_fields(self):

        from cost_intelligence.profitability_report import (
            ProfitabilityReport,
        )

        field_names = {
            field.name
            for field in fields(ProfitabilityReport)
        }

        self.assertEqual(
            field_names,
            {
                "production_cost",
                "selling_price",
                "gross_profit",
                "gross_margin_rate",
                "profitability_status",
                "currency",
                "warnings",
            },
        )

    def test_profitability_report_has_safe_defaults(self):

        from cost_intelligence.profitability_report import (
            ProfitabilityReport,
        )

        report = ProfitabilityReport()

        self.assertEqual(report.production_cost, 0.0)
        self.assertEqual(report.selling_price, 0.0)
        self.assertEqual(report.gross_profit, 0.0)
        self.assertEqual(report.gross_margin_rate, 0.0)
        self.assertEqual(report.profitability_status, "UNKNOWN")
        self.assertEqual(report.currency, "MAD")
        self.assertEqual(report.warnings, [])


if __name__ == "__main__":
    unittest.main()
