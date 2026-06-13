import unittest


class TestHardwareCostCalculator(unittest.TestCase):

    def test_hardware_cost_calculator_exists(self):

        try:
            from cost_intelligence.hardware_cost_calculator import (
                HardwareCostCalculator,
            )
        except ImportError:
            self.fail(
                "HardwareCostCalculator does not exist"
            )

    def test_hardware_cost_calculator_estimates_quantity_times_unit_price(self):

        from cost_intelligence.hardware_cost_calculator import (
            HardwareCostCalculator,
        )

        hardware_items = [
            {
                "sku": "HINGE_STD",
                "quantity": 4,
            }
        ]

        pricing_catalog = {
            "HINGE_STD": {
                "unit_price": 12,
                "currency": "MAD",
            }
        }

        result = HardwareCostCalculator().estimate(
            hardware_items=hardware_items,
            pricing_catalog=pricing_catalog,
        )

        self.assertEqual(
            result.hardware_cost,
            48,
        )

        self.assertEqual(
            result.total_cost,
            48,
        )

    def test_hardware_cost_calculator_warns_when_sku_price_is_missing(self):

        from cost_intelligence.hardware_cost_calculator import (
            HardwareCostCalculator,
        )

        result = HardwareCostCalculator().estimate(
            hardware_items=[
                {
                    "sku": "HANDLE_MISSING",
                    "quantity": 2,
                }
            ],
            pricing_catalog={},
        )

        self.assertEqual(
            result.warnings,
            [
                "Missing hardware price for HANDLE_MISSING",
            ],
        )


if __name__ == "__main__":
    unittest.main()
