import unittest
from dataclasses import fields, is_dataclass


class TestQuotationBreakdownReportContract(unittest.TestCase):

    def test_report_is_dataclass(self):
        from cost_intelligence.quotation_breakdown_report import (
            QuotationBreakdownReport,
        )

        self.assertTrue(is_dataclass(QuotationBreakdownReport))

    def test_report_has_exact_field_order(self):
        from cost_intelligence.quotation_breakdown_report import (
            QuotationBreakdownReport,
        )

        self.assertEqual(
            [field.name for field in fields(QuotationBreakdownReport)],
            [
                "material_cost",
                "sheet_cost",
                "waste_cost",
                "hardware_cost",
                "edge_banding_cost",
                "machining_cost",
                "panel_handling_cost",
                "manufacturing_cost",
                "markup_amount",
                "selling_price",
                "currency",
            ],
        )

    def test_report_has_safe_defaults(self):
        from cost_intelligence.quotation_breakdown_report import (
            QuotationBreakdownReport,
        )

        report = QuotationBreakdownReport()

        self.assertEqual(report.material_cost, 0.0)
        self.assertEqual(report.sheet_cost, 0.0)
        self.assertEqual(report.waste_cost, 0.0)
        self.assertEqual(report.hardware_cost, 0.0)
        self.assertEqual(report.edge_banding_cost, 0.0)
        self.assertEqual(report.machining_cost, 0.0)
        self.assertEqual(report.panel_handling_cost, 0.0)
        self.assertEqual(report.manufacturing_cost, 0.0)
        self.assertEqual(report.markup_amount, 0.0)
        self.assertEqual(report.selling_price, 0.0)
        self.assertEqual(report.currency, "MAD")


if __name__ == "__main__":
    unittest.main()
