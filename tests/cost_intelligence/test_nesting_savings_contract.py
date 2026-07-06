"""
OI-BS-2A: Nesting Alternative Savings Comparison
==================================================

Contract tests proving:
  - report and builder exist and are minimal
  - identical reports produce zero deltas
  - improved alternative shows positive savings
  - worse alternative shows negative savings
  - recovered value delta is correctly signed
  - profitability delta = total cost delta
  - builder consumes existing reports only (no recalculation)
"""

import unittest
from dataclasses import fields, is_dataclass


class TestNestingSavingsContract(unittest.TestCase):
    """Contract tests for NestingSavingsReport and NestingSavingsBuilder."""

    def _make_cost_report(self, **overrides):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        return ManufacturingCostReport(**overrides)

    # ── report contract ──────────────────────────────────────────────────

    def test_savings_report_is_dataclass(self):
        from cost_intelligence.nesting_savings_report import (
            NestingSavingsReport,
        )

        self.assertTrue(is_dataclass(NestingSavingsReport))

    def test_savings_report_has_required_fields(self):
        from cost_intelligence.nesting_savings_report import (
            NestingSavingsReport,
        )

        names = [f.name for f in fields(NestingSavingsReport)]

        self.assertIn("material_savings", names)
        self.assertIn("waste_reduction", names)
        self.assertIn("recovered_value_delta", names)
        self.assertIn("total_manufacturing_cost_delta", names)
        self.assertIn("profitability_delta", names)

    def test_savings_report_defaults(self):
        from cost_intelligence.nesting_savings_report import (
            NestingSavingsReport,
        )

        report = NestingSavingsReport()

        self.assertEqual(report.material_savings, 0.0)
        self.assertEqual(report.waste_reduction, 0.0)
        self.assertEqual(report.recovered_value_delta, 0.0)
        self.assertEqual(report.total_manufacturing_cost_delta, 0.0)
        self.assertEqual(report.profitability_delta, 0.0)

    def test_builder_exists(self):
        from cost_intelligence.nesting_savings_builder import (
            NestingSavingsBuilder,
        )

        self.assertTrue(callable(NestingSavingsBuilder().build))

    # ── identical reports → zero deltas ─────────────────────────────────

    def test_identical_reports_produce_zero_deltas(self):
        from cost_intelligence.nesting_savings_builder import (
            NestingSavingsBuilder,
        )

        report = self._make_cost_report(
            material_cost=800.0,
            sheet_cost=1000.0,
            waste_cost=200.0,
            recovered_value=50.0,
            net_material_cost=950.0,
            total_manufacturing_cost=1500.0,
        )

        savings = NestingSavingsBuilder().build(report, report)

        self.assertEqual(savings.material_savings, 0.0)
        self.assertEqual(savings.waste_reduction, 0.0)
        self.assertEqual(savings.recovered_value_delta, 0.0)
        self.assertEqual(savings.total_manufacturing_cost_delta, 0.0)
        self.assertEqual(savings.profitability_delta, 0.0)

    # ── improved alternative → positive savings ─────────────────────────

    def test_improved_alternative_shows_positive_savings(self):
        from cost_intelligence.nesting_savings_builder import (
            NestingSavingsBuilder,
        )

        current = self._make_cost_report(
            material_cost=800.0,
            sheet_cost=1200.0,
            waste_cost=400.0,
            recovered_value=50.0,
            net_material_cost=1150.0,
            total_manufacturing_cost=1800.0,
        )
        improved = self._make_cost_report(
            material_cost=800.0,
            sheet_cost=1000.0,
            waste_cost=200.0,
            recovered_value=100.0,
            net_material_cost=900.0,
            total_manufacturing_cost=1500.0,
        )

        savings = NestingSavingsBuilder().build(current, improved)

        # material savings = 1150 - 900 = 250
        self.assertEqual(savings.material_savings, 250.0)
        # waste reduction = 400 - 200 = 200
        self.assertEqual(savings.waste_reduction, 200.0)
        # recovered value delta = 100 - 50 = 50 (alternative recovered more)
        self.assertEqual(savings.recovered_value_delta, 50.0)
        # total cost delta = 1800 - 1500 = 300
        self.assertEqual(savings.total_manufacturing_cost_delta, 300.0)
        # profitability delta = same as total cost delta
        self.assertEqual(savings.profitability_delta, 300.0)

    # ── worse alternative → negative savings ────────────────────────────

    def test_worse_alternative_shows_negative_savings(self):
        from cost_intelligence.nesting_savings_builder import (
            NestingSavingsBuilder,
        )

        current = self._make_cost_report(
            sheet_cost=1000.0,
            waste_cost=200.0,
            net_material_cost=1000.0,
            total_manufacturing_cost=1500.0,
        )
        worse = self._make_cost_report(
            sheet_cost=1300.0,
            waste_cost=500.0,
            net_material_cost=1300.0,
            total_manufacturing_cost=1800.0,
        )

        savings = NestingSavingsBuilder().build(current, worse)

        self.assertLess(savings.material_savings, 0.0)
        self.assertLess(savings.waste_reduction, 0.0)
        self.assertLess(savings.total_manufacturing_cost_delta, 0.0)
        self.assertLess(savings.profitability_delta, 0.0)

    # ── recovered value delta correctly signed ──────────────────────────

    def test_recovered_value_delta_positive_when_alternative_recovers_more(self):
        from cost_intelligence.nesting_savings_builder import (
            NestingSavingsBuilder,
        )

        current = self._make_cost_report(recovered_value=50.0)
        improved = self._make_cost_report(recovered_value=120.0)

        savings = NestingSavingsBuilder().build(current, improved)

        # Alternative recovers 70 more → positive delta
        self.assertEqual(savings.recovered_value_delta, 70.0)

    def test_recovered_value_delta_negative_when_current_recovers_more(self):
        from cost_intelligence.nesting_savings_builder import (
            NestingSavingsBuilder,
        )

        current = self._make_cost_report(recovered_value=100.0)
        improved = self._make_cost_report(recovered_value=30.0)

        savings = NestingSavingsBuilder().build(current, improved)

        self.assertEqual(savings.recovered_value_delta, -70.0)

    # ── profitability delta = total cost delta ──────────────────────────

    def test_profitability_delta_equals_total_cost_delta(self):
        from cost_intelligence.nesting_savings_builder import (
            NestingSavingsBuilder,
        )

        current = self._make_cost_report(total_manufacturing_cost=2000.0)
        alternative = self._make_cost_report(total_manufacturing_cost=1600.0)

        savings = NestingSavingsBuilder().build(current, alternative)

        self.assertEqual(savings.total_manufacturing_cost_delta, 400.0)
        self.assertEqual(savings.profitability_delta, 400.0)

    # ── builder consumes existing reports only ──────────────────────────

    def test_builder_accepts_any_object_with_required_fields(self):
        """The builder must accept any object with the required fields,
        not just ManufacturingCostReport specifically."""
        from cost_intelligence.nesting_savings_builder import (
            NestingSavingsBuilder,
        )
        from types import SimpleNamespace

        current = SimpleNamespace(
            net_material_cost=1000.0,
            waste_cost=200.0,
            recovered_value=50.0,
            total_manufacturing_cost=1600.0,
        )
        alternative = SimpleNamespace(
            net_material_cost=800.0,
            waste_cost=100.0,
            recovered_value=80.0,
            total_manufacturing_cost=1300.0,
        )

        savings = NestingSavingsBuilder().build(current, alternative)

        self.assertEqual(savings.material_savings, 200.0)
        self.assertEqual(savings.total_manufacturing_cost_delta, 300.0)

    def test_builder_handles_missing_fields_gracefully(self):
        from cost_intelligence.nesting_savings_builder import (
            NestingSavingsBuilder,
        )
        from types import SimpleNamespace

        current = SimpleNamespace(total_manufacturing_cost=1000.0)
        alternative = SimpleNamespace(total_manufacturing_cost=800.0)

        savings = NestingSavingsBuilder().build(current, alternative)

        # Missing fields should default to 0.0
        self.assertEqual(savings.material_savings, 0.0)
        self.assertEqual(savings.total_manufacturing_cost_delta, 200.0)

    # ── no recalculation: end-to-end with real reports ──────────────────

    def test_end_to_end_with_real_cost_reports(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )
        from cost_intelligence.nesting_savings_builder import (
            NestingSavingsBuilder,
        )

        ctx = ManufacturingCostContext(total_panel_area_m2=5.0)

        current = ManufacturingCostCalculator().calculate(
            ctx, sheet_cost=1000.0, recovered_value=50.0,
        )
        improved = ManufacturingCostCalculator().calculate(
            ctx, sheet_cost=800.0, recovered_value=120.0,
        )

        savings = NestingSavingsBuilder().build(current, improved)

        # current material = 600 (cut part), sheet = 1000, waste = 400, net = 950
        self.assertEqual(current.net_material_cost, 950.0)
        # improved: material = 600, sheet = 800, waste = 200, net = 680
        self.assertEqual(improved.net_material_cost, 680.0)
        # savings: 950 - 680 = 270
        self.assertEqual(savings.material_savings, 270.0)
        # waste reduction: 400 - 200 = 200
        self.assertEqual(savings.waste_reduction, 200.0)
        # recovered: 120 - 50 = 70
        self.assertEqual(savings.recovered_value_delta, 70.0)
        # total: current=950, improved=680, delta=270
        self.assertEqual(savings.total_manufacturing_cost_delta, 270.0)
        self.assertEqual(savings.profitability_delta, 270.0)


if __name__ == "__main__":
    unittest.main()
