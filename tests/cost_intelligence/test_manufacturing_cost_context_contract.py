import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingCostContextContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        self.assertTrue(is_dataclass(ManufacturingCostContext))

    def test_contract_has_required_fields(self):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingCostContext)],
            [
                "total_panels",
                "total_panel_area_m2",
                "total_edge_meters",
                "total_drilling_operations",
                "total_material_types",
                "warnings_count",
                "warnings",
            ],
        )

    def test_contract_defaults(self):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        context = ManufacturingCostContext()

        self.assertEqual(context.total_panels, 0)
        self.assertEqual(context.total_panel_area_m2, 0.0)
        self.assertEqual(context.total_edge_meters, 0.0)
        self.assertEqual(context.total_drilling_operations, 0)
        self.assertEqual(context.total_material_types, 0)
        self.assertEqual(context.warnings_count, 0)
        self.assertEqual(context.warnings, [])

    def test_warning_defaults_are_independent(self):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        first_context = ManufacturingCostContext()
        second_context = ManufacturingCostContext()

        self.assertIsNot(first_context.warnings, second_context.warnings)


if __name__ == "__main__":
    unittest.main()
