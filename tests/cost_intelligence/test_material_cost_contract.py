import unittest


class TestMaterialCostContract(unittest.TestCase):

    def test_material_cost_contract_exists(self):

        try:
            from cost_intelligence.material_cost_calculator import (
                MaterialCostCalculator,
            )
        except ImportError:
            self.fail(
                "MaterialCostCalculator does not exist"
            )



    def test_material_cost_calculator_has_estimate_method(self):

        from cost_intelligence.material_cost_calculator import (
            MaterialCostCalculator,
        )

        calculator = MaterialCostCalculator()

        self.assertTrue(
            hasattr(
                calculator,
                "estimate",
            )
        )


    def test_material_cost_calculator_estimates_single_item_by_area(self):

        from exports.cutlist_engine import CutListItem
        from cost_intelligence.material_cost_calculator import (
            MaterialCostCalculator,
        )

        item = CutListItem(
            identity="P1",
            width=1000,
            height=500,
            thickness=18,
            material="MDF",
            group="TEST",
            role="SHELF",
            quantity=1,
        )

        pricing_catalog = {
            "MDF_18MM": {
                "price_per_m2": 100,
                "currency": "MAD",
            }
        }

        result = MaterialCostCalculator().estimate(
            cutlist_items=[item],
            pricing_catalog=pricing_catalog,
        )

        self.assertEqual(
            result.material_cost,
            50,
        )

        self.assertEqual(
            result.total_cost,
            50,
        )


    def test_material_cost_calculator_respects_quantity(self):

        from exports.cutlist_engine import CutListItem
        from cost_intelligence.material_cost_calculator import (
            MaterialCostCalculator,
        )

        item = CutListItem(
            identity="P1",
            width=1000,
            height=500,
            thickness=18,
            material="MDF",
            group="TEST",
            role="SHELF",
            quantity=3,
        )

        pricing_catalog = {
            "MDF_18MM": {
                "price_per_m2": 100,
                "currency": "MAD",
            }
        }

        result = MaterialCostCalculator().estimate(
            cutlist_items=[item],
            pricing_catalog=pricing_catalog,
        )

        self.assertEqual(
            result.material_cost,
            150,
        )

        self.assertEqual(
            result.total_cost,
            150,
        )


    def test_material_cost_calculator_returns_cost_estimate(self):

        from cost_intelligence.material_cost_calculator import (
            MaterialCostCalculator,
        )

        from cost_intelligence.cost_estimate import (
            CostEstimate,
        )

        result = MaterialCostCalculator().estimate(
            [],
            {},
        )

        self.assertIsInstance(
            result,
            CostEstimate,
        )


    def test_material_cost_calculator_warns_when_price_is_missing(self):

        from exports.cutlist_engine import CutListItem
        from cost_intelligence.material_cost_calculator import (
            MaterialCostCalculator,
        )

        item = CutListItem(
            identity="P1",
            width=1000,
            height=500,
            thickness=18,
            material="UNKNOWN",
            group="TEST",
            role="SHELF",
            quantity=1,
        )

        result = MaterialCostCalculator().estimate(
            cutlist_items=[item],
            pricing_catalog={},
        )

        self.assertEqual(
            result.material_cost,
            0,
        )

        self.assertTrue(
            result.warnings,
        )


    def test_material_cost_calculator_accepts_pricing_catalog_object(self):

        from exports.cutlist_engine import CutListItem
        from cost_intelligence.material_cost_calculator import (
            MaterialCostCalculator,
        )
        from cost_intelligence.pricing_catalog import (
            PricingCatalog,
        )

        item = CutListItem(
            identity="P1",
            width=1000,
            height=500,
            thickness=18,
            material="MDF",
            group="TEST",
            role="SHELF",
            quantity=1,
        )

        pricing_catalog = PricingCatalog(
            {
                "MDF_18MM": {
                    "price_per_m2": 100,
                    "currency": "MAD",
                }
            }
        )

        result = MaterialCostCalculator().estimate(
            cutlist_items=[item],
            pricing_catalog=pricing_catalog,
        )

        self.assertEqual(
            result.material_cost,
            50,
        )

if __name__ == "__main__":
    unittest.main()
