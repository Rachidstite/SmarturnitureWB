import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingCostRulesContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        self.assertTrue(is_dataclass(ManufacturingCostRules))

    def test_contract_has_required_fields(self):
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingCostRules)],
            [
                "material_area_rate",
                "edge_meter_rate",
                "drilling_rate",
                "complexity_material_type_rate",
                "panel_handling_rate",
                "operation_rates",
                "currency",
            ],
        )

    def test_contract_defaults(self):
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        rules = ManufacturingCostRules()

        self.assertEqual(rules.material_area_rate, 120.0)
        self.assertEqual(rules.edge_meter_rate, 5.0)
        self.assertEqual(rules.drilling_rate, 1.5)
        self.assertEqual(rules.complexity_material_type_rate, 25.0)
        self.assertEqual(rules.panel_handling_rate, 0.0)
        self.assertEqual(rules.operation_rates, {})
        self.assertEqual(rules.currency, "MAD")


if __name__ == "__main__":
    unittest.main()
