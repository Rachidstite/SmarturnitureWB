import unittest


class TestQuotationDocumentExport(unittest.TestCase):

    def test_exporter_exists(self):
        from exports.quotation_document_export import QuotationDocumentExport

        self.assertTrue(callable(QuotationDocumentExport.render_text))

    def test_render_text_returns_string(self):
        from exports.quotation_document_export import QuotationDocumentExport

        text = QuotationDocumentExport.render_text(self._document())

        self.assertIsInstance(text, str)

    def test_render_text_includes_all_customer_fields(self):
        from exports.quotation_document_export import QuotationDocumentExport

        text = QuotationDocumentExport.render_text(self._document())

        self.assertIn("Quotation: Q-2026-001", text)
        self.assertIn("Issue Date: 2026-06-15", text)
        self.assertIn("Valid Until: 2026-07-15", text)
        self.assertIn("Seller: Smart Furniture", text)
        self.assertIn("Customer: Example Customer", text)
        self.assertIn("Project: Custom wardrobe", text)
        self.assertIn("Total: 12500.0 MAD", text)
        self.assertIn("Notes: Installation included", text)
        self.assertIn("Payment Terms: 50% deposit", text)

    def test_render_text_excludes_internal_fields(self):
        from exports.quotation_document_export import QuotationDocumentExport

        text = QuotationDocumentExport.render_text(self._document())

        self.assertNotIn("production_cost", text)
        self.assertNotIn("markup_rate", text)
        self.assertNotIn("markup_amount", text)
        self.assertNotIn("gross_profit", text)
        self.assertNotIn("gross_margin_rate", text)
        self.assertNotIn("warnings", text)

    def test_render_text_handles_empty_optional_fields(self):
        from exports.quotation_document_export import QuotationDocumentExport

        document = self._document(notes="", payment_terms="")

        text = QuotationDocumentExport.render_text(document)

        self.assertIn("Notes: ", text)
        self.assertIn("Payment Terms: ", text)

    def test_render_text_does_not_mutate_document(self):
        from exports.quotation_document_export import QuotationDocumentExport

        document = self._document()
        original_values = document.__dict__.copy()

        QuotationDocumentExport.render_text(document)

        self.assertEqual(document.__dict__, original_values)


    def test_render_breakdown_text_includes_customer_and_cost_breakdown(self):
        from exports.quotation_document_export import QuotationDocumentExport
        from cost_intelligence.quotation_breakdown_report import (
            QuotationBreakdownReport,
        )

        breakdown = QuotationBreakdownReport(
            material_cost=1000.0,
            sheet_cost=800.0,
            waste_cost=50.0,
            hardware_cost=120.0,
            edge_banding_cost=60.0,
            machining_cost=90.0,
            panel_handling_cost=40.0,
            manufacturing_cost=2160.0,
            markup_amount=540.0,
            selling_price=2700.0,
            currency="MAD",
        )

        text = QuotationDocumentExport.render_breakdown_text(
            self._document(),
            breakdown,
        )

        self.assertIn("Quotation: Q-2026-001", text)
        self.assertIn("Customer: Example Customer", text)
        self.assertIn("Project: Custom wardrobe", text)
        self.assertIn("Material Cost: 1000.0 MAD", text)
        self.assertIn("Sheet Cost: 800.0 MAD", text)
        self.assertIn("Waste Cost: 50.0 MAD", text)
        self.assertIn("Hardware Cost: 120.0 MAD", text)
        self.assertIn("Edge Banding Cost: 60.0 MAD", text)
        self.assertIn("Machining Cost: 90.0 MAD", text)
        self.assertIn("Panel Handling Cost: 40.0 MAD", text)
        self.assertIn("Manufacturing Cost: 2160.0 MAD", text)
        self.assertIn("Markup Amount: 540.0 MAD", text)
        self.assertIn("Selling Price: 2700.0 MAD", text)

    def test_render_breakdown_text_does_not_mutate_inputs(self):
        from exports.quotation_document_export import QuotationDocumentExport
        from cost_intelligence.quotation_breakdown_report import (
            QuotationBreakdownReport,
        )

        document = self._document()
        breakdown = QuotationBreakdownReport(
            material_cost=1000.0,
            selling_price=2700.0,
            currency="MAD",
        )

        original_document_values = document.__dict__.copy()
        original_breakdown_values = breakdown.__dict__.copy()

        QuotationDocumentExport.render_breakdown_text(document, breakdown)

        self.assertEqual(document.__dict__, original_document_values)
        self.assertEqual(breakdown.__dict__, original_breakdown_values)


    @staticmethod
    def _document(notes="Installation included", payment_terms="50% deposit"):
        from cost_intelligence.quotation_document import QuotationDocumentV1

        return QuotationDocumentV1(
            quotation_number="Q-2026-001",
            issue_date="2026-06-15",
            valid_until="2026-07-15",
            seller_name="Smart Furniture",
            customer_name="Example Customer",
            project_description="Custom wardrobe",
            total_amount=12500.0,
            currency="MAD",
            notes=notes,
            payment_terms=payment_terms,
        )


if __name__ == "__main__":
    unittest.main()
