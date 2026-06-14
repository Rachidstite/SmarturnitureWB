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

    def test_edge_banding_breakdown_uses_catalog_price_per_meter(self):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        context = ManufacturingCostContext(
            total_edge_meters=100,
            edge_meters_by_banding={
                "ABS_1MM": 10,
                "PVC_2MM": 5,
            },
        )
        pricing_catalog = {
            "ABS_1MM": {
                "price_per_meter": 5,
            },
            "PVC_2MM": {
                "price_per_meter": 9,
            },
        }

        report = self.calculator.calculate(
            context,
            pricing_catalog=pricing_catalog,
        )

        self.assertEqual(report.edge_banding_cost, 95)
        self.assertEqual(report.total_manufacturing_cost, 95)

    def test_missing_edge_banding_catalog_price_uses_rule_fallback(self):
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
            ManufacturingCostRules(edge_meter_rate=7)
        )
        context = ManufacturingCostContext(
            total_edge_meters=15,
            edge_meters_by_banding={
                "ABS_1MM": 10,
                "PVC_2MM": 5,
            },
        )
        pricing_catalog = {
            "ABS_1MM": {
                "price_per_meter": 5,
            },
        }

        report = calculator.calculate(
            context,
            pricing_catalog=pricing_catalog,
        )

        self.assertEqual(report.edge_banding_cost, 85)

    def test_empty_edge_banding_breakdown_preserves_legacy_calculation(self):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        context = ManufacturingCostContext(
            total_edge_meters=20,
            edge_meters_by_banding={},
        )
        pricing_catalog = {
            "ABS_1MM": {
                "price_per_meter": 100,
            },
        }

        report = self.calculator.calculate(
            context,
            pricing_catalog=pricing_catalog,
        )

        self.assertEqual(report.edge_banding_cost, 100)


if __name__ == "__main__":
    unittest.main()
