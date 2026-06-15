import unittest
from dataclasses import fields, is_dataclass


class TestQuotationDocumentContract(unittest.TestCase):

    def test_quotation_document_v1_exists_and_is_dataclass(self):
        from cost_intelligence.quotation_document import QuotationDocumentV1

        self.assertTrue(is_dataclass(QuotationDocumentV1))

    def test_quotation_document_v1_has_exact_field_order(self):
        from cost_intelligence.quotation_document import QuotationDocumentV1

        self.assertEqual(
            [field.name for field in fields(QuotationDocumentV1)],
            [
                "quotation_number",
                "issue_date",
                "valid_until",
                "seller_name",
                "customer_name",
                "project_description",
                "total_amount",
                "currency",
                "notes",
                "payment_terms",
            ],
        )

    def test_quotation_document_v1_has_safe_defaults(self):
        from cost_intelligence.quotation_document import QuotationDocumentV1

        document = QuotationDocumentV1()

        self.assertEqual(document.quotation_number, "")
        self.assertEqual(document.issue_date, "")
        self.assertEqual(document.valid_until, "")
        self.assertEqual(document.seller_name, "")
        self.assertEqual(document.customer_name, "")
        self.assertEqual(document.project_description, "")
        self.assertEqual(document.total_amount, 0.0)
        self.assertEqual(document.currency, "MAD")
        self.assertEqual(document.notes, "")
        self.assertEqual(document.payment_terms, "")

    def test_quotation_document_v1_accepts_customer_facing_data(self):
        from cost_intelligence.quotation_document import QuotationDocumentV1

        document = QuotationDocumentV1(
            quotation_number="Q-2026-001",
            issue_date="2026-06-15",
            valid_until="2026-07-15",
            seller_name="Smart Furniture",
            customer_name="Example Customer",
            project_description="Custom wardrobe",
            total_amount=12500.0,
            currency="MAD",
            notes="Installation included",
            payment_terms="50% deposit",
        )

        self.assertEqual(document.quotation_number, "Q-2026-001")
        self.assertEqual(document.issue_date, "2026-06-15")
        self.assertEqual(document.valid_until, "2026-07-15")
        self.assertEqual(document.seller_name, "Smart Furniture")
        self.assertEqual(document.customer_name, "Example Customer")
        self.assertEqual(document.project_description, "Custom wardrobe")
        self.assertEqual(document.total_amount, 12500.0)
        self.assertEqual(document.currency, "MAD")
        self.assertEqual(document.notes, "Installation included")
        self.assertEqual(document.payment_terms, "50% deposit")

    def test_quotation_document_v1_excludes_internal_commercial_fields(self):
        from cost_intelligence.quotation_document import QuotationDocumentV1

        field_names = {field.name for field in fields(QuotationDocumentV1)}

        self.assertNotIn("production_cost", field_names)
        self.assertNotIn("markup_rate", field_names)
        self.assertNotIn("gross_profit", field_names)
        self.assertNotIn("gross_margin_rate", field_names)


if __name__ == "__main__":
    unittest.main()
