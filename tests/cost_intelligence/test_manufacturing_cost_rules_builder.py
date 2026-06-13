import unittest


class TestManufacturingCostRulesBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.manufacturing_cost_rules_builder import (
            ManufacturingCostRulesBuilder,
        )

        self.assertTrue(callable(ManufacturingCostRulesBuilder().default))

    def test_default_returns_manufacturing_cost_rules(self):
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )
        from cost_intelligence.manufacturing_cost_rules_builder import (
            ManufacturingCostRulesBuilder,
        )

        rules = ManufacturingCostRulesBuilder().default()

        self.assertIsInstance(rules, ManufacturingCostRules)
        self.assertEqual(rules.material_area_rate, 120.0)
        self.assertEqual(rules.edge_meter_rate, 5.0)
        self.assertEqual(rules.drilling_rate, 1.5)
        self.assertEqual(rules.complexity_material_type_rate, 25.0)
        self.assertEqual(rules.currency, "MAD")


if __name__ == "__main__":
    unittest.main()
