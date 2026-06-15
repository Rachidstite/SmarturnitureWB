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
