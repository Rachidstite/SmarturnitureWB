"""
CI-BS-3: Factory Overhead Cost
===============================

Contract tests proving:
  - overhead_cost field exists on ManufacturingCostReport
  - default overhead is zero
  - existing total_manufacturing_cost remains unchanged with default rules
  - flat overhead increases total by exact flat amount
  - percentage overhead increases total by exact percentage of base cost
  - flat + percentage overhead combine correctly
  - labor cost is included in base cost before percentage overhead
  - overhead does not mutate warnings
  - calculate(context) remains backward compatible
  - pricing_catalog behavior remains unchanged
  - operation-specific rates still work with overhead
"""

import unittest
from dataclasses import fields


class TestFactoryOverheadContract(unittest.TestCase):
    """Contract tests for factory overhead cost integration."""

    def _make_context(self, **overrides):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        return ManufacturingCostContext(**overrides)

    def _make_labor_report(self, **overrides):
        from manufacturing.labor_cost_report import LaborCostReport

        return LaborCostReport(**overrides)

    # ── 1. overhead_cost field exists on ManufacturingCostReport ─────────

    def test_overhead_cost_field_exists_on_report(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        names = [f.name for f in fields(ManufacturingCostReport)]

        self.assertIn("overhead_cost", names)

    # ── 2. default overhead is zero ─────────────────────────────────────

    def test_default_overhead_is_zero(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        report = ManufacturingCostReport()

        self.assertEqual(report.overhead_cost, 0.0)

    def test_default_rules_produce_zero_overhead(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )

        context = self._make_context(total_panel_area_m2=5.0)
        report = ManufacturingCostCalculator().calculate(context)

        self.assertEqual(report.overhead_cost, 0.0)

    def test_overhead_flat_and_percentage_default_to_zero_in_rules(self):
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        rules = ManufacturingCostRules()

        self.assertEqual(rules.overhead_flat_cost, 0.0)
        self.assertEqual(rules.overhead_percentage, 0.0)

    # ── 3. existing total unchanged with default rules ───────────────────

    def test_total_manufacturing_cost_unchanged_with_default_overhead(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )

        context = self._make_context(
            total_panel_area_m2=10.0,
            total_edge_meters=20.0,
            total_drilling_operations=30,
            total_material_types=4,
        )
        report = ManufacturingCostCalculator().calculate(context)

        # Known baseline: material=1200 + edge=100 + drilling=45 + comp=100 = 1445
        self.assertEqual(report.total_manufacturing_cost, 1445.0)
        self.assertEqual(report.overhead_cost, 0.0)

    # ── 4. flat overhead increases total by exact amount ─────────────────

    def test_flat_overhead_increases_total_by_exact_amount(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(total_panel_area_m2=5.0)
        rules = ManufacturingCostRules(overhead_flat_cost=200.0)

        report = ManufacturingCostCalculator(rules).calculate(context)

        # material = 5.0 * 120 = 600
        # overhead = 200 (flat)
        self.assertEqual(report.overhead_cost, 200.0)
        self.assertEqual(report.total_manufacturing_cost, 800.0)

    # ── 5. percentage overhead increases total by exact percentage ───────

    def test_percentage_overhead_increases_total_by_exact_percent_of_base(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(total_panel_area_m2=5.0)
        rules = ManufacturingCostRules(overhead_percentage=0.15)  # 15%

        report = ManufacturingCostCalculator(rules).calculate(context)

        # material = 5.0 * 120 = 600
        # base = 600  (no other costs)
        # overhead = 600 * 0.15 = 90
        self.assertEqual(report.overhead_cost, 90.0)
        self.assertEqual(report.total_manufacturing_cost, 690.0)

    # ── 6. flat + percentage combine correctly ───────────────────────────

    def test_flat_and_percentage_overhead_combine(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(total_panel_area_m2=10.0)
        rules = ManufacturingCostRules(
            overhead_flat_cost=150.0,
            overhead_percentage=0.10,  # 10%
        )

        report = ManufacturingCostCalculator(rules).calculate(context)

        # material = 10.0 * 120 = 1200
        # base = 1200
        # overhead = 150 + (1200 * 0.10) = 150 + 120 = 270
        self.assertEqual(report.overhead_cost, 270.0)
        self.assertEqual(report.total_manufacturing_cost, 1470.0)

    # ── 7. labor cost included in base for percentage overhead ───────────

    def test_labor_cost_included_in_base_for_percentage_overhead(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(total_panel_area_m2=5.0)
        labor = self._make_labor_report(
            cnc_labor_cost=40.0,
            drilling_labor_cost=20.0,
            edge_banding_labor_cost=10.0,
            assembly_labor_cost=30.0,
            total_labor_cost=100.0,
        )
        rules = ManufacturingCostRules(overhead_percentage=0.20)  # 20%

        report = ManufacturingCostCalculator(rules).calculate(
            context, labor_cost_report=labor
        )

        # material = 600
        # labor = 100
        # base = 700
        # overhead = 700 * 0.20 = 140.0
        self.assertEqual(report.overhead_cost, 140.0)
        self.assertEqual(report.total_labor_cost, 100.0)

    def test_labor_in_base_same_as_no_labor_case(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        # With labor: 600 + 100 = 700 base → overhead = 700 * 0.10 = 70 → total = 770
        ctx = self._make_context(total_panel_area_m2=5.0)
        labor = self._make_labor_report(total_labor_cost=100.0)
        rules = ManufacturingCostRules(overhead_percentage=0.10)

        with_labor = ManufacturingCostCalculator(rules).calculate(
            ctx, labor_cost_report=labor
        )
        without_labor = ManufacturingCostCalculator(rules).calculate(ctx)

        self.assertEqual(with_labor.overhead_cost, 70.0)
        self.assertEqual(without_labor.overhead_cost, 60.0)
        # The difference in overhead is exactly 10% of the labor cost
        self.assertEqual(
            with_labor.overhead_cost - without_labor.overhead_cost,
            10.0,  # 10% of 100 = 10
        )

    # ── 8. overhead does not mutate warnings ─────────────────────────────

    def test_overhead_does_not_mutate_warnings(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        original_warnings = ["Test warning"]
        context = ManufacturingCostContext(
            total_panel_area_m2=5.0,
            warnings=list(original_warnings),
        )
        rules = ManufacturingCostRules(overhead_flat_cost=100.0)

        report = ManufacturingCostCalculator(rules).calculate(context)

        self.assertEqual(context.warnings, original_warnings)
        self.assertIn("Test warning", report.warnings)
        self.assertEqual(report.overhead_cost, 100.0)

    # ── 9. calculate(context) remains backward compatible ────────────────

    def test_calculate_context_only_still_works(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )

        context = self._make_context(
            total_panel_area_m2=10.0,
            total_edge_meters=20.0,
            total_drilling_operations=30,
            total_material_types=4,
        )
        report = ManufacturingCostCalculator().calculate(context)

        self.assertEqual(report.material_cost, 1200.0)
        self.assertEqual(report.edge_banding_cost, 100.0)
        self.assertEqual(report.drilling_cost, 45.0)
        self.assertEqual(report.complexity_cost, 100.0)
        self.assertEqual(report.total_manufacturing_cost, 1445.0)
        self.assertEqual(report.overhead_cost, 0.0)

    def test_calculate_with_hardware_cost_and_labor_with_overhead(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(total_panel_area_m2=5.0)
        labor = self._make_labor_report(total_labor_cost=100.0)
        rules = ManufacturingCostRules(overhead_percentage=0.10)

        report = ManufacturingCostCalculator(rules).calculate(
            context,
            hardware_cost=50.0,
            labor_cost_report=labor,
        )

        # base = 600 + 50 + 100 = 750
        # overhead = 750 * 0.10 = 75
        # total = 750 + 75 = 825
        self.assertEqual(report.hardware_cost, 50.0)
        self.assertEqual(report.total_labor_cost, 100.0)
        self.assertEqual(report.material_cost, 600.0)
        self.assertEqual(report.overhead_cost, 75.0)
        self.assertEqual(report.total_manufacturing_cost, 825.0)

    # ── 10. pricing_catalog behavior remains unchanged ───────────────────

    def test_pricing_catalog_still_works_with_overhead(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(
            total_edge_meters=100,
            edge_meters_by_banding={"ABS_1MM": 10, "PVC_2MM": 5},
        )
        pricing_catalog = {
            "ABS_1MM": {"price_per_meter": 5},
            "PVC_2MM": {"price_per_meter": 9},
        }
        rules = ManufacturingCostRules(overhead_flat_cost=50.0)

        report = ManufacturingCostCalculator(rules).calculate(
            context,
            pricing_catalog=pricing_catalog,
        )

        # edge = 10*5 + 5*9 = 95
        # base = 95
        # overhead = 50
        # total = 145
        self.assertEqual(report.edge_banding_cost, 95)
        self.assertEqual(report.overhead_cost, 50.0)
        self.assertEqual(report.total_manufacturing_cost, 145.0)

    # ── 11. operation-specific rates still work with overhead ────────────

    def test_operation_specific_rates_work_with_overhead(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(
            machining_operations_by_type={
                "DRILL": 10,
                "ROUTE": 5,
            },
        )
        rules = ManufacturingCostRules(
            drilling_rate=1.5,
            operation_rates={"ROUTE": 4.0},
            overhead_percentage=0.10,  # 10%
        )

        report = ManufacturingCostCalculator(rules).calculate(context)

        # DRILL: 10 * 1.5 = 15
        # ROUTE: 5 * 4.0 = 20
        # drilling_cost = 35
        # base = 35
        # overhead = 35 * 0.10 = 3.5
        self.assertEqual(report.drilling_cost, 35.0)
        self.assertEqual(report.overhead_cost, 3.5)
        self.assertEqual(report.total_manufacturing_cost, 38.5)


if __name__ == "__main__":
    unittest.main()
