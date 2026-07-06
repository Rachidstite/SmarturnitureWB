"""
OI-BS-1A: Waste/Sheet/Recovered Value Cost Pipeline Contract
==============================================================

Contract tests proving:
  - default sheet/waste/recovered/net material are zero
  - explicit values propagate to ManufacturingCostReport
  - net_material_cost = sheet_cost - recovered_value
  - totals include material impact exactly once
  - profitability reflects waste through total_manufacturing_cost
  - defaults preserve existing totals
  - no duplicate calculators/builders/pipelines introduced
"""

import inspect
import unittest
from types import SimpleNamespace


class TestWasteCostPipelineContract(unittest.TestCase):
    """Contract tests for waste/sheet/recovered value cost integration."""

    def _make_context(self, **overrides):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        return ManufacturingCostContext(**overrides)

    # ── 1-4. Defaults ────────────────────────────────────────────────────

    def test_default_sheet_cost_is_zero(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )
        report = ManufacturingCostReport()
        self.assertEqual(report.sheet_cost, 0.0)

    def test_default_waste_cost_is_zero(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )
        report = ManufacturingCostReport()
        self.assertEqual(report.waste_cost, 0.0)

    def test_default_recovered_value_is_zero(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )
        report = ManufacturingCostReport()
        self.assertEqual(report.recovered_value, 0.0)

    def test_default_net_material_cost_remains_backward_compatible(self):
        """When no sheet/waste/recovery data is provided,
        net_material_cost must equal material_cost."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        context = self._make_context(total_panel_area_m2=5.0)
        report = ManufacturingCostCalculator().calculate(context)
        # material_cost = 5.0 * 120 = 600
        self.assertEqual(report.material_cost, 600.0)
        self.assertEqual(report.sheet_cost, 0.0)
        self.assertEqual(report.waste_cost, 0.0)
        self.assertEqual(report.recovered_value, 0.0)
        self.assertEqual(report.net_material_cost, 600.0)

    # ── 5-7. Explicit value propagation ──────────────────────────────────

    def test_explicit_sheet_cost_propagates_to_report(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        context = self._make_context(total_panel_area_m2=5.0)
        report = ManufacturingCostCalculator().calculate(
            context, sheet_cost=1000.0,
        )
        self.assertEqual(report.sheet_cost, 1000.0)
        # waste_cost = sheet - material = 1000 - 600 = 400
        self.assertEqual(report.waste_cost, 400.0)

    def test_explicit_waste_cost_propagates_when_no_sheet_cost(self):
        """When sheet_cost is NOT provided, the explicit waste_cost param
        must be used directly."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        context = self._make_context(total_panel_area_m2=5.0)
        report = ManufacturingCostCalculator().calculate(
            context, waste_cost=250.0,
        )
        self.assertEqual(report.waste_cost, 250.0)
        self.assertEqual(report.sheet_cost, 0.0)

    def test_explicit_recovered_value_propagates(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        context = self._make_context(total_panel_area_m2=5.0)
        report = ManufacturingCostCalculator().calculate(
            context, sheet_cost=1000.0, recovered_value=80.0,
        )
        self.assertEqual(report.recovered_value, 80.0)
        self.assertEqual(report.sheet_cost, 1000.0)

    # ── 8. net_material_cost formula ─────────────────────────────────────

    def test_net_material_cost_equals_sheet_minus_recovered(self):
        """When sheet_cost is provided, net_material_cost must be
        sheet_cost - recovered_value."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        context = self._make_context(total_panel_area_m2=10.0)
        report = ManufacturingCostCalculator().calculate(
            context,
            sheet_cost=2000.0,
            recovered_value=150.0,
        )
        self.assertEqual(report.net_material_cost, 1850.0)
        self.assertEqual(report.sheet_cost, 2000.0)

    def test_net_material_cost_equals_material_when_sheet_not_provided(self):
        """When no sheet_cost, net_material_cost must fall back to
        material_cost."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        context = self._make_context(total_panel_area_m2=10.0)
        report = ManufacturingCostCalculator().calculate(context)
        self.assertEqual(report.net_material_cost, report.material_cost)
        self.assertEqual(report.net_material_cost, 1200.0)

    # ── 9. total includes material impact exactly once ───────────────────

    def test_total_includes_sheet_cost_not_material_cost_when_provided(self):
        """When sheet_cost is provided, total_manufacturing_cost must use
        sheet_cost as the effective material — not the net cut-part
        material_cost."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        context = self._make_context(total_panel_area_m2=10.0)
        # No sheet: total = material (1200) = 1200
        no_sheet = ManufacturingCostCalculator().calculate(context)
        # With sheet=1500: total = sheet (1500) = 1500
        with_sheet = ManufacturingCostCalculator().calculate(
            context, sheet_cost=1500.0,
        )
        self.assertEqual(no_sheet.total_manufacturing_cost, 1200.0)
        self.assertEqual(with_sheet.total_manufacturing_cost, 1500.0)
        # Difference is exactly the sheet - material gap
        self.assertEqual(
            with_sheet.total_manufacturing_cost - no_sheet.total_manufacturing_cost,
            300.0,
        )

    def test_total_includes_recovered_value_as_credit(self):
        """Recovered value must reduce net_material_cost and
        total_manufacturing_cost."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        context = self._make_context(total_panel_area_m2=10.0)

        no_recovery = ManufacturingCostCalculator().calculate(
            context, sheet_cost=2000.0, recovered_value=0.0,
        )
        with_recovery = ManufacturingCostCalculator().calculate(
            context, sheet_cost=2000.0, recovered_value=200.0,
        )

        self.assertEqual(no_recovery.total_manufacturing_cost, 2000.0)
        self.assertEqual(with_recovery.total_manufacturing_cost, 1800.0)
        self.assertEqual(
            no_recovery.total_manufacturing_cost - with_recovery.total_manufacturing_cost,
            200.0,
        )

    # ── 10. profitability reflects waste ─────────────────────────────────

    def test_profitability_reflects_waste_through_total(self):
        """Higher sheet_cost (i.e., worse nesting utilization) must
        increase production_cost through total_manufacturing_cost."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_summary_builder import (
            ManufacturingCostSummaryBuilder,
        )
        from cost_intelligence.manufacturing_cost_insights_builder import (
            ManufacturingCostInsightsBuilder,
        )
        from cost_intelligence.manufacturing_cost_risk_report_builder import (
            ManufacturingCostRiskReportBuilder,
        )
        from cost_intelligence.manufacturing_quotation_input_builder import (
            ManufacturingQuotationInputBuilder,
        )
        from cost_intelligence.manufacturing_quotation_report_builder import (
            ManufacturingQuotationReportBuilder,
        )
        from cost_intelligence.manufacturing_profitability_report_builder import (
            ManufacturingProfitabilityReportBuilder,
        )

        context = self._make_context(total_panel_area_m2=5.0)

        def run_pipeline(sheet_cost=0.0):
            cost_report = ManufacturingCostCalculator().calculate(
                context, sheet_cost=sheet_cost,
            )
            insights = ManufacturingCostInsightsBuilder().build(context)
            risk = ManufacturingCostRiskReportBuilder().build(insights)
            summary = ManufacturingCostSummaryBuilder().build(
                cost_report, risk, insights,
            )
            qi = ManufacturingQuotationInputBuilder().build(
                summary, markup_rate=0.25,
            )
            qr = ManufacturingQuotationReportBuilder().build(qi)
            pr = ManufacturingProfitabilityReportBuilder().build(qr)
            return qr, pr

        qr_efficient, pr_efficient = run_pipeline()  # sheet=0 → material=600
        qr_wasteful, pr_wasteful = run_pipeline(sheet_cost=900.0)

        # Efficient: production_cost=600, selling=750, profit=150
        self.assertEqual(qr_efficient.production_cost, 600.0)
        self.assertEqual(pr_efficient.gross_profit, 150.0)

        # Wasteful: production_cost=900, selling=1125, profit=225
        # (markup on higher cost = higher absolute profit)
        self.assertEqual(qr_wasteful.production_cost, 900.0)
        self.assertEqual(pr_wasteful.gross_profit, 225.0)

        # Production cost reflects the waste difference
        self.assertEqual(
            qr_wasteful.production_cost - qr_efficient.production_cost,
            300.0,
        )

    # ── 11. defaults preserve existing totals ────────────────────────────

    def test_defaults_preserve_existing_totals(self):
        """With all defaults (no sheet/waste/recovery), the total must
        match the pre-OI-BS-1A baseline."""
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
        self.assertEqual(report.sheet_cost, 0.0)
        self.assertEqual(report.waste_cost, 0.0)
        self.assertEqual(report.recovered_value, 0.0)
        self.assertEqual(report.net_material_cost, 1200.0)
        # Baseline: 1200 + 100 + 45 + 100 = 1445
        self.assertEqual(report.total_manufacturing_cost, 1445.0)

    # ── 12. no duplicate calculators/builders/pipelines ──────────────────

    def test_no_new_builders_in_pipeline_builder(self):
        """The cost pipeline builder must not import any optimization
        or waste-specific builder directly."""
        from cost_intelligence import manufacturing_cost_pipeline_builder as mod
        source = inspect.getsource(mod)
        self.assertNotIn("WasteCostCalculator", source)
        self.assertNotIn("SheetCostCalculator", source)
        self.assertNotIn("OffcutIntelligenceBuilder", source)
        self.assertNotIn("WasteIntelligenceBuilder", source)
        self.assertNotIn("NestingIntelligenceBuilder", source)

    def test_no_new_builders_in_calculator(self):
        """The cost calculator must not import any optimization
        or waste-specific calculator."""
        from cost_intelligence import manufacturing_cost_calculator as mod
        source = inspect.getsource(mod)
        self.assertNotIn("WasteCostCalculator", source)
        self.assertNotIn("SheetCostCalculator", source)
        self.assertNotIn("OffcutIntelligenceBuilder", source)
        self.assertNotIn("WasteIntelligenceBuilder", source)

    def test_pipeline_builder_passes_through_no_duplicate_calculation(self):
        """The pipeline builder must pass optimization data through
        to the calculator without computing anything itself."""
        from cost_intelligence.manufacturing_cost_pipeline_builder import (
            ManufacturingCostPipelineBuilder,
        )
        sig = inspect.signature(ManufacturingCostPipelineBuilder.build)
        self.assertIn("sheet_cost", sig.parameters)
        self.assertIn("waste_cost", sig.parameters)
        self.assertIn("recovered_value", sig.parameters)


if __name__ == "__main__":
    unittest.main()
