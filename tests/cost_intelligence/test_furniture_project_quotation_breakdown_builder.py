import unittest
from types import SimpleNamespace
from unittest.mock import patch


class TestFurnitureProjectQuotationBreakdownBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.furniture_project_quotation_breakdown_builder import (
            FurnitureProjectQuotationBreakdownBuilder,
        )

        self.assertTrue(callable(FurnitureProjectQuotationBreakdownBuilder().build))

    @patch(
        "cost_intelligence.furniture_project_quotation_breakdown_builder."
        "ManufacturingCommercialPipelineBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_quotation_breakdown_builder."
        "ManufacturingProductionPackageBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_quotation_breakdown_builder."
        "ManufacturingRuntimePipelineBuilder"
    )
    def test_builder_builds_simple_breakdown_for_each_cabinet(
        self,
        runtime_builder_class,
        production_package_builder_class,
        commercial_pipeline_builder_class,
    ):
        from cost_intelligence.furniture_project_quotation_breakdown_builder import (
            FurnitureProjectQuotationBreakdownBuilder,
        )
        from domain.furniture_project import FurnitureProject

        first_cabinet = SimpleNamespace(graph=object())
        second_cabinet = SimpleNamespace(graph=object())
        furniture_project = FurnitureProject(
            cabinets=[first_cabinet, second_cabinet]
        )

        runtime_builder_class.return_value.build.side_effect = [
            SimpleNamespace(manufacturing_package=object()),
            SimpleNamespace(manufacturing_package=object()),
        ]

        first_production_package = object()
        second_production_package = object()
        production_package_builder_class.return_value.build.side_effect = [
            first_production_package,
            second_production_package,
        ]

        commercial_pipeline_builder_class.return_value.build.side_effect = [
            SimpleNamespace(
                manufacturing_cost_summary=SimpleNamespace(
                    total_manufacturing_cost=1000.0,
                    risk_level="LOW",
                ),
                quotation_report=SimpleNamespace(
                    selling_price=1300.0,
                    currency="MAD",
                ),
            ),
            SimpleNamespace(
                manufacturing_cost_summary=SimpleNamespace(
                    total_manufacturing_cost=2000.0,
                    risk_level="MEDIUM",
                ),
                quotation_report=SimpleNamespace(
                    selling_price=2600.0,
                    currency="MAD",
                ),
            ),
        ]

        result = FurnitureProjectQuotationBreakdownBuilder().build(
            furniture_project,
            markup_rate=0.30,
            currency="MAD",
        )

        self.assertEqual(
            result,
            [
                {
                    "cabinet_index": 1,
                    "total_manufacturing_cost": 1000.0,
                    "selling_price": 1300.0,
                    "currency": "MAD",
                    "risk_level": "LOW",
                },
                {
                    "cabinet_index": 2,
                    "total_manufacturing_cost": 2000.0,
                    "selling_price": 2600.0,
                    "currency": "MAD",
                    "risk_level": "MEDIUM",
                },
            ],
        )
        commercial_pipeline_builder_class.return_value.build.assert_any_call(
            first_production_package,
            0.30,
            "MAD",
        )
        commercial_pipeline_builder_class.return_value.build.assert_any_call(
            second_production_package,
            0.30,
            "MAD",
        )

    def test_builder_returns_empty_list_for_empty_project(self):
        from cost_intelligence.furniture_project_quotation_breakdown_builder import (
            FurnitureProjectQuotationBreakdownBuilder,
        )
        from domain.furniture_project import FurnitureProject

        result = FurnitureProjectQuotationBreakdownBuilder().build(
            FurnitureProject()
        )

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
