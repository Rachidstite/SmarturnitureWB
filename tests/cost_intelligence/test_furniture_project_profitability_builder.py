import unittest
from unittest.mock import patch


class TestFurnitureProjectProfitabilityBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.furniture_project_profitability_builder import (
            FurnitureProjectProfitabilityBuilder,
        )

        self.assertTrue(callable(FurnitureProjectProfitabilityBuilder().build))

    @patch(
        "cost_intelligence.furniture_project_profitability_builder."
        "FurnitureProjectQuotationBreakdownBuilder"
    )
    def test_builder_calculates_project_profitability_from_breakdowns(
        self,
        breakdown_builder_class,
    ):
        from cost_intelligence.furniture_project_profitability_builder import (
            FurnitureProjectProfitabilityBuilder,
        )

        furniture_project = object()
        breakdown_builder_class.return_value.build.return_value = [
            {
                "total_manufacturing_cost": 1000.0,
                "selling_price": 1300.0,
                "currency": "MAD",
            },
            {
                "total_manufacturing_cost": 2000.0,
                "selling_price": 2600.0,
                "currency": "MAD",
            },
        ]

        result = FurnitureProjectProfitabilityBuilder().build(
            furniture_project,
            markup_rate=0.30,
            currency="MAD",
        )

        self.assertEqual(
            result,
            {
                "total_manufacturing_cost": 3000.0,
                "total_selling_price": 3900.0,
                "gross_profit": 900.0,
                "gross_margin_rate": 900.0 / 3900.0,
                "currency": "MAD",
            },
        )
        breakdown_builder_class.return_value.build.assert_called_once_with(
            furniture_project,
            markup_rate=0.30,
            currency="MAD",
        )

    def test_builder_handles_zero_selling_price(self):
        from cost_intelligence.furniture_project_profitability_builder import (
            FurnitureProjectProfitabilityBuilder,
        )

        result = FurnitureProjectProfitabilityBuilder()._build_report(
            breakdowns=[],
            currency="MAD",
        )

        self.assertEqual(result["total_manufacturing_cost"], 0.0)
        self.assertEqual(result["total_selling_price"], 0.0)
        self.assertEqual(result["gross_profit"], 0.0)
        self.assertEqual(result["gross_margin_rate"], 0.0)
        self.assertEqual(result["currency"], "MAD")


if __name__ == "__main__":
    unittest.main()
