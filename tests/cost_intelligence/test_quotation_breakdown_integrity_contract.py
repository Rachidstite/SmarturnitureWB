import unittest
from dataclasses import fields


class TestQuotationBreakdownIntegrityContract(unittest.TestCase):

    def test_report_exposes_current_core_cost_fields(self):
        from cost_intelligence.quotation_breakdown_report import (
            QuotationBreakdownReport,
        )

        field_names = [field.name for field in fields(QuotationBreakdownReport)]

        self.assertIn("material_cost", field_names)
        self.assertIn("hardware_cost", field_names)
        self.assertIn("edge_banding_cost", field_names)
        self.assertIn("machining_cost", field_names)

    def test_report_does_not_expose_postponed_categories_yet(self):
        from cost_intelligence.quotation_breakdown_report import (
            QuotationBreakdownReport,
        )

        field_names = [field.name for field in fields(QuotationBreakdownReport)]

        self.assertNotIn("labor_cost", field_names)
        self.assertNotIn("assembly_cost", field_names)
        self.assertNotIn("cnc_machine_cost", field_names)
        self.assertNotIn("delivery_cost", field_names)
        self.assertNotIn("installation_cost", field_names)
        self.assertNotIn("packing_cost", field_names)

    def test_builder_maps_core_cost_fields(self):
        from cost_intelligence.cost_report import CostReport
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )
        from cost_intelligence.quotation_breakdown_builder import (
            QuotationBreakdownBuilder,
        )
        from cost_intelligence.quotation_report import QuotationReport

        report = QuotationBreakdownBuilder().build(
            CostReport(
                material_cost=100.0,
                sheet_cost=0.0,
                waste_cost=0.0,
                hardware_cost=40.0,
                total_cost=140.0,
                currency="MAD",
            ),
            ManufacturingCostReport(
                edge_banding_cost=50.0,
                drilling_cost=60.0,
                panel_handling_cost=70.0,
                total_manufacturing_cost=550.0,
                currency="MAD",
            ),
            QuotationReport(
                production_cost=140.0,
                markup_rate=0.25,
                markup_amount=35.0,
                selling_price=175.0,
                currency="MAD",
            ),
        )

        self.assertEqual(report.hardware_cost, 40.0)
        self.assertEqual(report.edge_banding_cost, 50.0)
        self.assertEqual(report.machining_cost, 60.0)

    def test_builder_does_not_double_count_cost_report_total_cost_or_manufacturing_total(self):
        from cost_intelligence.cost_report import CostReport
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )
        from cost_intelligence.quotation_breakdown_builder import (
            QuotationBreakdownBuilder,
        )
        from cost_intelligence.quotation_report import QuotationReport

        cost_report = CostReport(
            material_cost=100.0,
            sheet_cost=0.0,
            waste_cost=0.0,
            hardware_cost=40.0,
            total_cost=140.0,
            currency="MAD",
        )
        manufacturing_cost_report = ManufacturingCostReport(
            edge_banding_cost=50.0,
            drilling_cost=60.0,
            panel_handling_cost=70.0,
            total_manufacturing_cost=999.0,
            currency="MAD",
        )
        quotation_report = QuotationReport(
            production_cost=140.0,
            markup_rate=0.25,
            markup_amount=35.0,
            selling_price=175.0,
            currency="MAD",
        )

        report = QuotationBreakdownBuilder().build(
            cost_report,
            manufacturing_cost_report,
            quotation_report,
        )

        self.assertEqual(report.manufacturing_cost, 999.0)
        self.assertNotEqual(report.manufacturing_cost, cost_report.total_cost)

    def test_report_and_builder_keep_production_cost_and_manufacturing_cost_separate(self):
        from cost_intelligence.quotation_breakdown_report import (
            QuotationBreakdownReport,
        )
        from cost_intelligence.quotation_report import QuotationReport

        quote_field_names = [field.name for field in fields(QuotationReport)]
        breakdown_field_names = [
            field.name for field in fields(QuotationBreakdownReport)
        ]

        self.assertIn("production_cost", quote_field_names)
        self.assertNotIn("production_cost", breakdown_field_names)
        self.assertIn("manufacturing_cost", breakdown_field_names)
        self.assertIn("selling_price", breakdown_field_names)

        from cost_intelligence.cost_report import CostReport
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )
        from cost_intelligence.quotation_breakdown_builder import (
            QuotationBreakdownBuilder,
        )
        from cost_intelligence.quotation_report import QuotationReport

        quotation_report = QuotationReport(
            production_cost=140.0,
            markup_rate=0.25,
            markup_amount=35.0,
            selling_price=175.0,
            currency="MAD",
        )
        report = QuotationBreakdownBuilder().build(
            CostReport(
                material_cost=100.0,
                hardware_cost=40.0,
                total_cost=140.0,
                currency="MAD",
            ),
            ManufacturingCostReport(
                edge_banding_cost=50.0,
                drilling_cost=60.0,
                total_manufacturing_cost=550.0,
                currency="MAD",
            ),
            quotation_report,
        )

        self.assertEqual(report.manufacturing_cost, 550.0)
        self.assertEqual(report.selling_price, quotation_report.selling_price)
        self.assertNotIn("production_cost", breakdown_field_names)
        self.assertFalse(hasattr(report, "production_cost"))


if __name__ == "__main__":
    unittest.main()
