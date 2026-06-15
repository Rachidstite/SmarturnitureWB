import unittest


class TestQuotationBreakdownBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.quotation_breakdown_builder import (
            QuotationBreakdownBuilder,
        )

        self.assertTrue(callable(QuotationBreakdownBuilder().build))

    def test_builder_returns_quotation_breakdown_report(self):
        from cost_intelligence.quotation_breakdown_report import (
            QuotationBreakdownReport,
        )

        report = self._build()

        self.assertIsInstance(report, QuotationBreakdownReport)

    def test_builder_maps_all_fields_correctly(self):
        report = self._build()

        self.assertEqual(report.material_cost, 100.0)
        self.assertEqual(report.sheet_cost, 200.0)
        self.assertEqual(report.waste_cost, 30.0)
        self.assertEqual(report.hardware_cost, 40.0)
        self.assertEqual(report.edge_banding_cost, 50.0)
        self.assertEqual(report.machining_cost, 60.0)
        self.assertEqual(report.panel_handling_cost, 70.0)
        self.assertEqual(report.manufacturing_cost, 550.0)
        self.assertEqual(report.markup_amount, 150.0)
        self.assertEqual(report.selling_price, 700.0)
        self.assertEqual(report.currency, "EUR")

    def test_builder_does_not_mutate_cost_report(self):
        builder, cost_report, manufacturing_cost_report, quotation_report = (
            self._inputs()
        )
        original_values = cost_report.__dict__.copy()
        original_warnings = cost_report.warnings

        builder.build(cost_report, manufacturing_cost_report, quotation_report)

        self.assertEqual(cost_report.__dict__, original_values)
        self.assertIs(cost_report.warnings, original_warnings)

    def test_builder_does_not_mutate_manufacturing_cost_report(self):
        builder, cost_report, manufacturing_cost_report, quotation_report = (
            self._inputs()
        )
        original_values = manufacturing_cost_report.__dict__.copy()
        original_warnings = manufacturing_cost_report.warnings

        builder.build(cost_report, manufacturing_cost_report, quotation_report)

        self.assertEqual(manufacturing_cost_report.__dict__, original_values)
        self.assertIs(manufacturing_cost_report.warnings, original_warnings)

    def test_builder_does_not_mutate_quotation_report(self):
        builder, cost_report, manufacturing_cost_report, quotation_report = (
            self._inputs()
        )
        original_values = quotation_report.__dict__.copy()
        original_warnings = quotation_report.warnings

        builder.build(cost_report, manufacturing_cost_report, quotation_report)

        self.assertEqual(quotation_report.__dict__, original_values)
        self.assertIs(quotation_report.warnings, original_warnings)

    @classmethod
    def _build(cls):
        builder, cost_report, manufacturing_cost_report, quotation_report = (
            cls._inputs()
        )
        return builder.build(
            cost_report,
            manufacturing_cost_report,
            quotation_report,
        )

    @staticmethod
    def _inputs():
        from cost_intelligence.cost_report import CostReport
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )
        from cost_intelligence.quotation_breakdown_builder import (
            QuotationBreakdownBuilder,
        )
        from cost_intelligence.quotation_report import QuotationReport

        return (
            QuotationBreakdownBuilder(),
            CostReport(
                material_cost=100.0,
                sheet_cost=200.0,
                waste_cost=30.0,
                hardware_cost=40.0,
                warnings=["Cost warning"],
            ),
            ManufacturingCostReport(
                edge_banding_cost=50.0,
                drilling_cost=60.0,
                panel_handling_cost=70.0,
                total_manufacturing_cost=550.0,
                warnings=["Manufacturing cost warning"],
            ),
            QuotationReport(
                markup_amount=150.0,
                selling_price=700.0,
                currency="EUR",
                warnings=["Quotation warning"],
            ),
        )


if __name__ == "__main__":
    unittest.main()
