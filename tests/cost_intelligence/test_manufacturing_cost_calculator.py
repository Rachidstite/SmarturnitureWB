import unittest


class TestManufacturingCostCalculator(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )

        self.calculator = ManufacturingCostCalculator()

    def test_calculator_exists(self):
        self.assertTrue(callable(self.calculator.calculate))

    def test_calculate_returns_fixed_rate_manufacturing_cost_report(self):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        warnings = ["Manufacturing warnings detected"]
        context = ManufacturingCostContext(
            total_panel_area_m2=10.0,
            total_edge_meters=20.0,
            total_drilling_operations=30,
            total_material_types=4,
            warnings=warnings,
        )

        report = self.calculator.calculate(context)

        self.assertIsInstance(report, ManufacturingCostReport)
        self.assertEqual(report.material_cost, 1200.0)
        self.assertEqual(report.edge_banding_cost, 100.0)
        self.assertEqual(report.drilling_cost, 45.0)
        self.assertEqual(report.complexity_cost, 100.0)
        self.assertEqual(report.total_manufacturing_cost, 1445.0)
        self.assertEqual(report.currency, "MAD")
        self.assertIs(report.warnings, warnings)

    def test_zero_context_returns_zero_manufacturing_cost(self):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        report = self.calculator.calculate(ManufacturingCostContext())

        self.assertEqual(report.material_cost, 0.0)
        self.assertEqual(report.edge_banding_cost, 0.0)
        self.assertEqual(report.drilling_cost, 0.0)
        self.assertEqual(report.complexity_cost, 0.0)
        self.assertEqual(report.total_manufacturing_cost, 0.0)

    def test_custom_rules_change_calculation(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        calculator = ManufacturingCostCalculator(
            ManufacturingCostRules(
                material_area_rate=200,
                edge_meter_rate=10,
                drilling_rate=2,
                complexity_material_type_rate=50,
                currency="MAD",
            )
        )
        context = ManufacturingCostContext(
            total_panel_area_m2=2,
            total_edge_meters=3,
            total_drilling_operations=4,
            total_material_types=1,
        )

        report = calculator.calculate(context)

        self.assertEqual(report.material_cost, 400)
        self.assertEqual(report.edge_banding_cost, 30)
        self.assertEqual(report.drilling_cost, 8)
        self.assertEqual(report.complexity_cost, 50)
        self.assertEqual(report.total_manufacturing_cost, 488)
        self.assertEqual(report.currency, "MAD")


if __name__ == "__main__":
    unittest.main()
