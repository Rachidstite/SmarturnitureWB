import unittest
from dataclasses import fields


class TestQuotationDocumentBuilderV1(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.quotation_document_builder import (
            QuotationDocumentBuilderV1,
        )

        self.assertTrue(callable(QuotationDocumentBuilderV1().build))

    def test_build_returns_quotation_document_v1(self):
        from cost_intelligence.quotation_document import QuotationDocumentV1

        document = self._build_document()

        self.assertIsInstance(document, QuotationDocumentV1)

    def test_build_maps_selling_price_to_total_amount(self):
        document = self._build_document(selling_price=1250.0)

        self.assertEqual(document.total_amount, 1250.0)

    def test_build_maps_currency(self):
        document = self._build_document(currency="EUR")

        self.assertEqual(document.currency, "EUR")

    def test_build_maps_required_metadata(self):
        document = self._build_document(
            quotation_number="Q-2026-001",
            issue_date="2026-06-15",
            valid_until="2026-07-15",
            seller_name="Smart Furniture",
            customer_name="Example Customer",
            project_description="Custom wardrobe",
        )

        self.assertEqual(document.quotation_number, "Q-2026-001")
        self.assertEqual(document.issue_date, "2026-06-15")
        self.assertEqual(document.valid_until, "2026-07-15")
        self.assertEqual(document.seller_name, "Smart Furniture")
        self.assertEqual(document.customer_name, "Example Customer")
        self.assertEqual(document.project_description, "Custom wardrobe")

    def test_build_defaults_notes_and_payment_terms(self):
        document = self._build_document()

        self.assertEqual(document.notes, "")
        self.assertEqual(document.payment_terms, "")

    def test_build_does_not_mutate_quotation_report(self):
        from cost_intelligence.quotation_document_builder import (
            QuotationDocumentBuilderV1,
        )
        from cost_intelligence.quotation_report import QuotationReport

        warnings = ["Internal warning"]
        quotation_report = QuotationReport(
            production_cost=1000.0,
            markup_rate=0.25,
            markup_amount=250.0,
            selling_price=1250.0,
            currency="EUR",
            warnings=warnings,
        )
        original_values = quotation_report.__dict__.copy()

        self._build(QuotationDocumentBuilderV1(), quotation_report)

        self.assertEqual(quotation_report.__dict__, original_values)
        self.assertIs(quotation_report.warnings, warnings)

    def test_document_does_not_expose_production_cost(self):
        document = self._build_document()
        field_names = {field.name for field in fields(document)}

        self.assertNotIn("production_cost", field_names)
        self.assertFalse(hasattr(document, "production_cost"))

    def test_document_does_not_expose_markup_rate(self):
        document = self._build_document()
        field_names = {field.name for field in fields(document)}

        self.assertNotIn("markup_rate", field_names)
        self.assertFalse(hasattr(document, "markup_rate"))

    def test_build_works_when_quotation_report_contains_warnings(self):
        from cost_intelligence.quotation_document_builder import (
            QuotationDocumentBuilderV1,
        )
        from cost_intelligence.quotation_report import QuotationReport

        quotation_report = QuotationReport(
            selling_price=1250.0,
            currency="MAD",
            warnings=["Internal manufacturing warning"],
        )

        document = self._build(QuotationDocumentBuilderV1(), quotation_report)

        self.assertEqual(document.total_amount, 1250.0)
        self.assertFalse(hasattr(document, "warnings"))

    def _build_document(
        self,
        selling_price=1000.0,
        currency="MAD",
        quotation_number="Q-001",
        issue_date="2026-06-15",
        valid_until="2026-07-15",
        seller_name="Seller",
        customer_name="Customer",
        project_description="Project",
    ):
        from cost_intelligence.quotation_document_builder import (
            QuotationDocumentBuilderV1,
        )
        from cost_intelligence.quotation_report import QuotationReport

        quotation_report = QuotationReport(
            selling_price=selling_price,
            currency=currency,
        )
        return self._build(
            QuotationDocumentBuilderV1(),
            quotation_report,
            quotation_number=quotation_number,
            issue_date=issue_date,
            valid_until=valid_until,
            seller_name=seller_name,
            customer_name=customer_name,
            project_description=project_description,
        )

    @staticmethod
    def _build(
        builder,
        quotation_report,
        quotation_number="Q-001",
        issue_date="2026-06-15",
        valid_until="2026-07-15",
        seller_name="Seller",
        customer_name="Customer",
        project_description="Project",
    ):
        return builder.build(
            quotation_report,
            quotation_number=quotation_number,
            issue_date=issue_date,
            valid_until=valid_until,
            seller_name=seller_name,
            customer_name=customer_name,
            project_description=project_description,
        )


if __name__ == "__main__":
    unittest.main()
