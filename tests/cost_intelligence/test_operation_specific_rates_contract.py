"""
CI-BS-2: Operation-Specific Manufacturing Rates
================================================

Contract tests proving:
  - existing projects behave identically with default rates
  - operation-specific rates override defaults correctly
  - totals remain deterministic
  - backward compatibility preserved
"""

import unittest
from dataclasses import fields


class TestOperationSpecificRatesContract(unittest.TestCase):
    """Contract tests for operation-specific machining rates."""

    # ── helpers ──────────────────────────────────────────────────────────

    def _make_context(self, **overrides):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        return ManufacturingCostContext(**overrides)

    # ── 1. existing projects behave identically with default rates ───────

    def test_operation_rates_defaults_to_empty_dict(self):
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        rules = ManufacturingCostRules()

        self.assertEqual(rules.operation_rates, {})

    def test_empty_operation_rates_produces_identical_machining_cost(self):
        """With empty operation_rates, the calculator must behave
        exactly as before — using drilling_rate as the only fallback."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(
            total_drilling_operations=0,
            machining_operations_by_type={
                "DRILL": 10,
                "ROUTE": 2,
            },
        )

        rules_with_operation_rates = ManufacturingCostRules(
            drilling_rate=1.5,
            operation_rates={},
        )
        calculator = ManufacturingCostCalculator(rules_with_operation_rates)

        # All operation types fall back to drilling_rate=1.5
        report = calculator.calculate(context)

        # 12 operations * 1.5 = 18.0
        self.assertEqual(report.drilling_cost, 18.0)
        self.assertEqual(report.total_manufacturing_cost, 18.0)

        # Compare with original rules (no operation_rates field)
        from cost_intelligence.manufacturing_cost_rules_builder import (
            ManufacturingCostRulesBuilder,
        )

        original_calculator = ManufacturingCostCalculator(
            ManufacturingCostRulesBuilder().default()
        )
        original_report = original_calculator.calculate(context)
        self.assertEqual(report.drilling_cost, original_report.drilling_cost)
        self.assertEqual(
            report.total_manufacturing_cost,
            original_report.total_manufacturing_cost,
        )

    def test_operation_rates_field_present_on_rules_dataclass(self):
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        names = [f.name for f in fields(ManufacturingCostRules)]

        self.assertIn("operation_rates", names)

    def test_default_rules_produces_same_network_cost_as_before(self):
        """Full pipeline without operation_rates must match baseline."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules_builder import (
            ManufacturingCostRulesBuilder,
        )

        default_rules = ManufacturingCostRulesBuilder().default()
        self.assertEqual(default_rules.operation_rates, {})

        context = self._make_context(
            total_panels=1,
            total_panel_area_m2=5.0,
            total_edge_meters=10.0,
            total_drilling_operations=10,
            total_material_types=2,
            machining_operations_by_type={"DRILL": 8, "ROUTE": 2},
        )

        report = ManufacturingCostCalculator(default_rules).calculate(context)

        # 8 DRILL + 2 ROUTE = 10 operations × 1.5 (drilling_rate) = 15.0
        self.assertEqual(report.drilling_cost, 15.0)
        self.assertAlmostEqual(report.material_cost, 600.0)
        self.assertEqual(report.edge_banding_cost, 50.0)
        self.assertEqual(report.complexity_cost, 50.0)
        self.assertEqual(report.panel_handling_cost, 0.0)

    # ── 2. operation-specific rates override defaults correctly ──────────

    def test_operation_specific_rate_overrides_drilling_fallback(self):
        """When operation_rates has a type-specific rate, it must be used
        instead of the generic drilling_rate."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(
            total_drilling_operations=0,
            machining_operations_by_type={
                "ROUTE": 10,
                "DRILL": 5,
            },
        )

        rules = ManufacturingCostRules(
            drilling_rate=1.5,  # generic fallback
            operation_rates={
                "ROUTE": 4.0,  # routing is more expensive
            },
        )
        report = ManufacturingCostCalculator(rules).calculate(context)

        # ROUTE: 10 × 4.0 = 40.0
        # DRILL: 5 × 1.5 (drilling_rate fallback) = 7.5
        # total: 47.5
        self.assertEqual(report.drilling_cost, 47.5)

    def test_multiple_operation_specific_rates(self):
        """Multiple operation types with different rates must all apply
        independently."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(
            machining_operations_by_type={
                "DRILL": 20,
                "HINGE_CUP": 4,
                "ROUT_GROOVE": 6,
                "SLOT": 2,
            },
        )

        rules = ManufacturingCostRules(
            drilling_rate=1.5,
            operation_rates={
                "HINGE_CUP": 3.5,
                "ROUT_GROOVE": 2.8,
                "SLOT": 2.0,
            },
        )
        report = ManufacturingCostCalculator(rules).calculate(context)

        # DRILL:      20 × 1.5 (drilling_rate fallback) = 30.0
        # HINGE_CUP:   4 × 3.5                          = 14.0
        # ROUT_GROOVE: 6 × 2.8                          = 16.8
        # SLOT:        2 × 2.0                          = 4.0
        # total: 64.8
        self.assertEqual(report.drilling_cost, 64.8)

    # ── 3. totals remain deterministic ───────────────────────────────────

    def test_deterministic_with_same_inputs(self):
        """Same inputs must produce identical results every time."""
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
                "HINGE_CUP": 2,
            },
        )
        rules = ManufacturingCostRules(
            drilling_rate=2.0,
            operation_rates={"ROUTE": 3.0, "HINGE_CUP": 4.0},
        )

        first = ManufacturingCostCalculator(rules).calculate(context).drilling_cost
        second = ManufacturingCostCalculator(rules).calculate(context).drilling_cost

        self.assertEqual(first, second)

    def test_ordering_of_operation_types_does_not_affect_total(self):
        """The calculator must produce the same total regardless of
        iteration order in machining_operations_by_type."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        rules = ManufacturingCostRules(
            drilling_rate=1.5,
            operation_rates={"ROUTE": 3.0, "DRILL": 2.0},
        )

        # Different dict insertion order
        context_a = self._make_context(
            machining_operations_by_type=dict(
                sorted({"DRILL": 10, "ROUTE": 5}.items())
            ),
        )
        context_b = self._make_context(
            machining_operations_by_type=dict(
                reversed(list({"DRILL": 10, "ROUTE": 5}.items()))
            ),
        )

        calc = ManufacturingCostCalculator(rules)
        total_a = calc.calculate(context_a).drilling_cost
        total_b = calc.calculate(context_b).drilling_cost

        self.assertEqual(total_a, total_b)

    # ── 4. backward compatibility preserved ──────────────────────────────

    def test_rules_without_operation_rates_machines_at_drilling_rate(self):
        """Original ManufacturingCostRules() without setting operation_rates
        must behave identically to before."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        # Original constructor pattern (no operation_rates)
        rules = ManufacturingCostRules(drilling_rate=1.5)
        context = self._make_context(
            total_drilling_operations=10,
            machining_operations_by_type={"DRILL": 8, "ROUTE": 2},
        )

        report = ManufacturingCostCalculator(rules).calculate(context)

        # All operations fall back to drilling_rate=1.5
        self.assertEqual(report.drilling_cost, 15.0)

    def test_pipeline_builder_uses_default_rules_without_operation_rates(self):
        """The ManufacturingCostPipelineBuilder must continue to work
        with default rules containing empty operation_rates."""
        from cost_intelligence.manufacturing_cost_pipeline_builder import (
            ManufacturingCostPipelineBuilder,
        )
        from manufacturing.manufacturing_cutlist_report import (
            ManufacturingCutlistReport,
        )
        from manufacturing.manufacturing_edge_report import ManufacturingEdgeReport
        from manufacturing.manufacturing_machining_report import (
            ManufacturingMachiningReport,
        )
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )
        from manufacturing.manufacturing_summary_report import (
            ManufacturingSummaryReport,
        )

        package = ManufacturingProductionPackage(
            cutlist_report=ManufacturingCutlistReport(
                items=[
                    {
                        "identity": "panel-01",
                        "width": 600.0,
                        "height": 800.0,
                        "thickness": 18.0,
                        "material": "MDF",
                        "quantity": 2,
                    }
                ],
                total_items=2,
                warnings=[],
            ),
            edge_report=ManufacturingEdgeReport(
                items=[],
                total_items=0,
                total_linear_meters=0.0,
                warnings=[],
            ),
            machining_report=ManufacturingMachiningReport(
                items=[
                    {
                        "operation_type": "DRILL",
                        "diameter": 5.0,
                        "depth": 12.0,
                        "is_through": False,
                        "x": 10.0,
                        "y": 20.0,
                        "z": 0.0,
                        "face": "TOP",
                        "axis": "Z",
                        "source": "panel-01",
                    },
                    {
                        "operation_type": "ROUTE",
                        "diameter": 6.0,
                        "depth": 5.0,
                        "is_through": False,
                        "x": 30.0,
                        "y": 40.0,
                        "z": 0.0,
                        "face": "TOP",
                        "axis": "Z",
                        "source": "panel-01",
                    },
                ],
                total_items=2,
                warnings=[],
            ),
            summary_report=ManufacturingSummaryReport(
                total_panels=2,
                total_materials=1,
                total_edge_operations=0,
                total_machining_operations=2,
                warnings=[],
            ),
            warnings=[],
        )

        summary = ManufacturingCostPipelineBuilder().build(package)

        cost = summary.cost_report
        self.assertGreater(cost.material_cost, 0.0)

    def test_operation_rates_are_independent_per_calculator_instance(self):
        """Different calculator instances with different operation_rates
        must not interfere with each other."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(
            machining_operations_by_type={"ROUTE": 5, "DRILL": 5},
        )

        calc_a = ManufacturingCostCalculator(
            ManufacturingCostRules(drilling_rate=1.0, operation_rates={"ROUTE": 5.0})
        )
        calc_b = ManufacturingCostCalculator(
            ManufacturingCostRules(drilling_rate=1.0, operation_rates={"ROUTE": 3.0})
        )

        report_a = calc_a.calculate(context)
        report_b = calc_b.calculate(context)

        # A: ROUTE=5*5.0 + DRILL=5*1.0 = 30
        # B: ROUTE=5*3.0 + DRILL=5*1.0 = 20
        self.assertEqual(report_a.drilling_cost, 30.0)
        self.assertEqual(report_b.drilling_cost, 20.0)


if __name__ == "__main__":
    unittest.main()
