import unittest
from types import SimpleNamespace
from unittest.mock import patch


class TestFurnitureProjectQuotationBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.furniture_project_quotation_builder import (
            FurnitureProjectQuotationBuilder,
        )

        self.assertTrue(callable(FurnitureProjectQuotationBuilder().build))

    @patch(
        "cost_intelligence.furniture_project_quotation_builder."
        "QuotationDocumentBuilderV1"
    )
    @patch(
        "cost_intelligence.furniture_project_quotation_builder."
        "ManufacturingCommercialPipelineBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_quotation_builder."
        "ManufacturingProductionPackageBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_quotation_builder."
        "FurnitureProjectManufacturingPackageBuilder"
    )
    def test_builder_delegates_to_existing_components_and_returns_document(
        self,
        project_package_builder_class,
        production_package_builder_class,
        commercial_pipeline_builder_class,
        quotation_document_builder_class,
    ):
        from cost_intelligence.furniture_project_quotation_builder import (
            FurnitureProjectQuotationBuilder,
        )

        furniture_project = object()
        manufacturing_package = object()
        manufacturing_production_package = object()
        quotation_report = object()
        quotation_document = object()

        project_package_builder_class.return_value.build.return_value = (
            manufacturing_package
        )
        production_package_builder_class.return_value.build.return_value = (
            manufacturing_production_package
        )
        commercial_pipeline_builder_class.return_value.build.return_value = (
            SimpleNamespace(quotation_report=quotation_report)
        )
        quotation_document_builder_class.return_value.build.return_value = (
            quotation_document
        )

        result = FurnitureProjectQuotationBuilder().build(
            furniture_project,
            quotation_number="Q-001",
            issue_date="2026-06-15",
            valid_until="2026-07-15",
            seller_name="Smart Furniture",
            customer_name="Example Customer",
            project_description="Kitchen project",
            markup_rate=0.25,
            currency="EUR",
            notes="Installation included",
            payment_terms="50% deposit",
        )

        project_package_builder_class.return_value.build.assert_called_once_with(
            furniture_project
        )
        production_package_builder_class.return_value.build.assert_called_once_with(
            manufacturing_package
        )
        commercial_pipeline_builder_class.return_value.build.assert_called_once_with(
            manufacturing_production_package,
            0.25,
            "EUR",
        )
        quotation_document_builder_class.return_value.build.assert_called_once_with(
            quotation_report,
            quotation_number="Q-001",
            issue_date="2026-06-15",
            valid_until="2026-07-15",
            seller_name="Smart Furniture",
            customer_name="Example Customer",
            project_description="Kitchen project",
            notes="Installation included",
            payment_terms="50% deposit",
        )
        self.assertIs(result, quotation_document)

    @patch(
        "cost_intelligence.furniture_project_quotation_builder."
        "QuotationDocumentBuilderV1"
    )
    @patch(
        "cost_intelligence.furniture_project_quotation_builder."
        "ManufacturingCommercialPipelineBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_quotation_builder."
        "ManufacturingProductionPackageBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_quotation_builder."
        "FurnitureProjectManufacturingPackageBuilder"
    )
    def test_builder_uses_defaults_and_does_not_mutate_furniture_project(
        self,
        project_package_builder_class,
        production_package_builder_class,
        commercial_pipeline_builder_class,
        quotation_document_builder_class,
    ):
        from cost_intelligence.furniture_project_quotation_builder import (
            FurnitureProjectQuotationBuilder,
        )
        from domain.furniture_project import FurnitureProject

        cabinets = [object()]
        metadata = {"customer": "Example"}
        furniture_project = FurnitureProject(
            project_id="PROJECT-1",
            name="Kitchen",
            cabinets=cabinets,
            metadata=metadata,
        )
        original_values = furniture_project.__dict__.copy()

        project_package_builder_class.return_value.build.return_value = object()
        production_package_builder_class.return_value.build.return_value = object()
        commercial_pipeline_builder_class.return_value.build.return_value = (
            SimpleNamespace(quotation_report=object())
        )

        FurnitureProjectQuotationBuilder().build(
            furniture_project,
            quotation_number="Q-001",
            issue_date="2026-06-15",
            valid_until="2026-07-15",
            seller_name="Smart Furniture",
            customer_name="Example Customer",
            project_description="Kitchen project",
        )

        commercial_pipeline_builder_class.return_value.build.assert_called_once()
        args = commercial_pipeline_builder_class.return_value.build.call_args.args
        self.assertEqual(args[1], 0.0)
        self.assertEqual(args[2], "MAD")

        document_call = quotation_document_builder_class.return_value.build.call_args
        self.assertEqual(document_call.kwargs["notes"], "")
        self.assertEqual(document_call.kwargs["payment_terms"], "")

        self.assertEqual(furniture_project.__dict__, original_values)
        self.assertIs(furniture_project.cabinets, cabinets)
        self.assertIs(furniture_project.metadata, metadata)


if __name__ == "__main__":
    unittest.main()
