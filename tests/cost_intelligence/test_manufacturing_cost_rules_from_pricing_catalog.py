import copy
import unittest


class TestManufacturingCostRulesFromPricingCatalog(unittest.TestCase):

    def test_default_rules_remain_unchanged(self):
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        rules = ManufacturingCostRules()

        self.assertEqual(rules.material_area_rate, 120.0)
        self.assertEqual(rules.edge_meter_rate, 5.0)
        self.assertEqual(rules.drilling_rate, 1.5)
        self.assertEqual(rules.complexity_material_type_rate, 25.0)
        self.assertEqual(rules.panel_handling_rate, 0.0)
        self.assertEqual(rules.currency, "MAD")

    def test_from_pricing_catalog_maps_material_edge_and_drilling_rates(self):
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        pricing_catalog = {
            "MDF_18MM": {
                "price_per_m2": 94.08,
            },
            "ABS_1MM": {
                "price_per_meter": 4.2,
            },
            "MACHINING_DRILL": {
                "price_per_operation": 2.75,
            },
        }

        rules = ManufacturingCostRules.from_pricing_catalog(pricing_catalog)

        self.assertEqual(rules.material_area_rate, 94.08)
        self.assertEqual(rules.edge_meter_rate, 4.2)
        self.assertEqual(rules.drilling_rate, 2.75)
        self.assertEqual(rules.complexity_material_type_rate, 25.0)
        self.assertEqual(rules.panel_handling_rate, 0.0)
        self.assertEqual(rules.currency, "MAD")

    def test_from_pricing_catalog_preserves_defaults_for_missing_values(self):
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        pricing_catalog = {
            "MDF_18MM": {},
            "ABS_1MM": {},
        }

        rules = ManufacturingCostRules.from_pricing_catalog(pricing_catalog)

        self.assertEqual(rules.material_area_rate, 120.0)
        self.assertEqual(rules.edge_meter_rate, 5.0)
        self.assertEqual(rules.drilling_rate, 1.5)
        self.assertEqual(rules.complexity_material_type_rate, 25.0)
        self.assertEqual(rules.panel_handling_rate, 0.0)
        self.assertEqual(rules.currency, "MAD")

    def test_from_pricing_catalog_uses_catalog_currency_when_present(self):
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        pricing_catalog = {
            "MDF_18MM": {
                "price_per_m2": 94.08,
                "currency": "EUR",
            },
            "ABS_1MM": {
                "price_per_meter": 4.2,
            },
        }

        rules = ManufacturingCostRules.from_pricing_catalog(pricing_catalog)

        self.assertEqual(rules.currency, "EUR")

    def test_from_pricing_catalog_does_not_mutate_input_catalog(self):
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        pricing_catalog = {
            "MDF_18MM": {
                "price_per_m2": 94.08,
                "currency": "EUR",
            },
            "ABS_1MM": {
                "price_per_meter": 4.2,
            },
            "MACHINING_DRILL": {
                "price_per_operation": 2.75,
            },
        }
        original_catalog = copy.deepcopy(pricing_catalog)

        ManufacturingCostRules.from_pricing_catalog(pricing_catalog)

        self.assertEqual(pricing_catalog, original_catalog)


if __name__ == "__main__":
    unittest.main()
