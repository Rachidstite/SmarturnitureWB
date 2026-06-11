import unittest


class TestSheetCostContractV1(unittest.TestCase):

    def test_sheet_cost_calculator_exists(self):

        try:
            from cost_intelligence.sheet_cost_calculator import (
                SheetCostCalculator,
            )
        except ImportError:
            self.fail(
                "SheetCostCalculator does not exist"
            )



    def test_sheet_cost_calculator_has_estimate_method(self):

        from cost_intelligence.sheet_cost_calculator import (
            SheetCostCalculator,
        )

        calculator = SheetCostCalculator()

        self.assertTrue(
            hasattr(
                calculator,
                "estimate",
            )
        )


    def test_sheet_cost_calculator_estimates_sheet_count_by_stock_key(self):

        from cost_intelligence.sheet_cost_calculator import (
            SheetCostCalculator,
        )

        nesting_results = {
            "MDF_18MM": [
                object(),
                object(),
            ]
        }

        pricing_catalog = {
            "MDF_18MM": {
                "price_per_sheet": 280,
                "currency": "MAD",
            }
        }

        result = SheetCostCalculator().estimate(
            nesting_results=nesting_results,
            pricing_catalog=pricing_catalog,
        )

        self.assertEqual(
            result.sheet_cost,
            560,
        )

        self.assertEqual(
            result.total_cost,
            560,
        )

if __name__ == "__main__":
    unittest.main()
