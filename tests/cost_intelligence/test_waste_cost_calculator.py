import unittest


class TestWasteCostCalculator(unittest.TestCase):

    def test_waste_cost_calculator_exists(self):

        try:
            from cost_intelligence.waste_cost_calculator import (
                WasteCostCalculator,
            )
        except ImportError:
            self.fail(
                "WasteCostCalculator does not exist"
            )



    def test_waste_cost_calculator_estimates_waste_from_ratio(self):

        from types import SimpleNamespace

        from cost_intelligence.waste_cost_calculator import (
            WasteCostCalculator,
        )

        sheet = SimpleNamespace(
            waste_ratio=0.30,
        )

        nesting_results = {
            "MDF_18MM": [
                sheet,
            ]
        }

        pricing_catalog = {
            "MDF_18MM": {
                "price_per_sheet": 280,
                "currency": "MAD",
            }
        }

        result = WasteCostCalculator().estimate(
            nesting_results=nesting_results,
            pricing_catalog=pricing_catalog,
        )

        self.assertEqual(
            result.waste_cost,
            84,
        )

        self.assertEqual(
            result.total_cost,
            84,
        )

if __name__ == "__main__":
    unittest.main()
