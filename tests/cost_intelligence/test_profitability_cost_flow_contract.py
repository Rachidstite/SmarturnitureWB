"""
COM-BS-1: Profitability Impact from Real Manufacturing Cost
=============================================================

Contract tests proving:
  - profitability reflects labor cost
  - profitability reflects overhead cost
  - profitability reflects operation-specific machining rates
    through total cost
  - commercial reports do not recompute cost
  - old zero/default behavior remains unchanged
"""

import unittest


class TestProfitabilityCostFlowContract(unittest.TestCase):
    """Contract tests proving ManufacturingCostReport improvements
    propagate through the commercial pipeline."""

    def _make_context(self, **overrides):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        return ManufacturingCostContext(**overrides)

    def _make_labor(self, **overrides):
        from manufacturing.labor_cost_report import LaborCostReport

        return LaborCostReport(**overrides)

    # ── helpers: build full pipeline ─────────────────────────────────────

    def _build_commercial_result(self, context, *,
                                 hardware_cost=0.0,
                                 labor_cost_report=None,
                                 rules=None,
                                 markup_rate=0.0,
                                 currency="MAD"):
        """Run the full cost + commercial pipeline for a given context."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_insights_builder import (
            ManufacturingCostInsightsBuilder,
        )
        from cost_intelligence.manufacturing_cost_risk_report_builder import (
            ManufacturingCostRiskReportBuilder,
        )
        from cost_intelligence.manufacturing_cost_summary_builder import (
            ManufacturingCostSummaryBuilder,
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
        from cost_intelligence.quotation_intelligence_builder import (
            QuotationIntelligenceBuilder,
        )

        calc = ManufacturingCostCalculator(rules)
        cost_report = calc.calculate(
            context,
            hardware_cost=hardware_cost,
            labor_cost_report=labor_cost_report,
        )
        insights = ManufacturingCostInsightsBuilder().build(context)
        risk_report = ManufacturingCostRiskReportBuilder().build(insights)
        summary = ManufacturingCostSummaryBuilder().build(
            cost_report, risk_report, insights
        )

        quotation_input = ManufacturingQuotationInputBuilder().build(
            summary, markup_rate=markup_rate, currency=currency
        )
        quotation_report = ManufacturingQuotationReportBuilder().build(
            quotation_input
        )
        profitability_report = ManufacturingProfitabilityReportBuilder().build(
            quotation_report
        )
        intelligence_report = QuotationIntelligenceBuilder().build(
            quotation_report, profitability_report
        )

        return {
            "cost_report": cost_report,
            "summary": summary,
            "quotation_input": quotation_input,
            "quotation_report": quotation_report,
            "profitability_report": profitability_report,
            "intelligence_report": intelligence_report,
        }

    # ── 1. profitability reflects labor cost ─────────────────────────────

    def test_profitability_reflects_labor_cost(self):
        """Adding labor cost must increase production_cost and
        reduce gross_profit."""
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(
            total_panel_area_m2=5.0,
        )
        labor = self._make_labor(
            cnc_labor_cost=40.0,
            drilling_labor_cost=20.0,
            edge_banding_labor_cost=10.0,
            assembly_labor_cost=30.0,
            total_labor_cost=100.0,
        )

        # Without labor
        result_no_labor = self._build_commercial_result(
            context,
            markup_rate=0.25,
        )
        # With labor
        result_with_labor = self._build_commercial_result(
            context,
            labor_cost_report=labor,
            markup_rate=0.25,
        )

        base_no_labor = result_no_labor["cost_report"].total_manufacturing_cost
        base_with_labor = result_with_labor["cost_report"].total_manufacturing_cost
        self.assertEqual(
            base_with_labor - base_no_labor,
            100.0,  # labor cost
        )

        # production_cost reflects the difference
        self.assertEqual(
            result_with_labor["quotation_report"].production_cost
            - result_no_labor["quotation_report"].production_cost,
            100.0,
        )

        # selling_price reflects the difference (marked up)
        self.assertEqual(
            result_with_labor["quotation_report"].selling_price
            - result_no_labor["quotation_report"].selling_price,
            125.0,  # 100 * 1.25
        )

    # ── 2. profitability reflects overhead cost ──────────────────────────

    def test_profitability_reflects_overhead_cost(self):
        """Adding factory overhead must increase production_cost
        and selling_price."""
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(total_panel_area_m2=5.0)

        rules_no_overhead = ManufacturingCostRules()
        rules_with_overhead = ManufacturingCostRules(overhead_flat_cost=200.0)

        result_no_oh = self._build_commercial_result(
            context,
            rules=rules_no_overhead,
            markup_rate=0.25,
        )
        result_with_oh = self._build_commercial_result(
            context,
            rules=rules_with_overhead,
            markup_rate=0.25,
        )

        # Production cost diff should be exactly the overhead
        self.assertEqual(
            result_with_oh["quotation_report"].production_cost
            - result_no_oh["quotation_report"].production_cost,
            200.0,
        )

        # Selling price diff should be marked-up overhead
        self.assertEqual(
            result_with_oh["quotation_report"].selling_price
            - result_no_oh["quotation_report"].selling_price,
            250.0,  # 200 * 1.25
        )

    # ── 3. profitability reflects operation-specific rates through total ─

    def test_profitability_reflects_operation_specific_rates(self):
        """Using higher operation-specific rates must increase
        production_cost."""
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(
            machining_operations_by_type={"ROUTE": 10, "DRILL": 5},
        )

        rules_flat = ManufacturingCostRules(drilling_rate=1.5)
        rules_operation = ManufacturingCostRules(
            drilling_rate=1.5,
            operation_rates={"ROUTE": 4.0},
        )

        flat = self._build_commercial_result(
            context, rules=rules_flat, markup_rate=0.25
        )
        operation = self._build_commercial_result(
            context, rules=rules_operation, markup_rate=0.25
        )

        # flat: 15 * 1.5 = 22.5
        # operation: 5*1.5 + 10*4.0 = 7.5 + 40 = 47.5
        # diff = 25.0
        self.assertEqual(
            operation["quotation_report"].production_cost
            - flat["quotation_report"].production_cost,
            25.0,
        )

    # ── 4. commercial reports do not recompute cost ──────────────────────

    def test_commercial_does_not_recompute_cost(self):
        """Commercial pipeline must consume total_manufacturing_cost
        directly without recomputing components."""
        from cost_intelligence.manufacturing_quotation_input import (
            ManufacturingQuotationInput,
        )

        context = self._make_context(total_panel_area_m2=5.0)
        result = self._build_commercial_result(context, markup_rate=0.25)

        quotation_input = result["quotation_input"]

        # base_cost must equal total_manufacturing_cost directly
        self.assertEqual(
            quotation_input.base_cost,
            result["summary"].total_manufacturing_cost,
        )

        # quotation_input stores the summary — no cost recomputation
        self.assertIs(
            quotation_input.manufacturing_cost_summary,
            result["summary"],
        )

    def test_profitability_uses_production_cost_not_raw_components(self):
        """ProfitabilityCalculator must derive gross profit from
        production_cost, not from individual cost components."""
        from cost_intelligence.profitability_calculator import (
            ProfitabilityCalculator,
        )

        context = self._make_context(
            total_panel_area_m2=5.0,
            total_edge_meters=10.0,
            total_drilling_operations=5,
        )
        result = self._build_commercial_result(
            context,
            markup_rate=0.30,
        )

        profitability = result["profitability_report"]
        quotation = result["quotation_report"]

        # gross_profit = selling_price - production_cost
        self.assertEqual(
            profitability.gross_profit,
            quotation.selling_price - quotation.production_cost,
        )

        # profitability should NOT have access to individual cost components
        self.assertFalse(hasattr(profitability, "material_cost"))
        self.assertFalse(hasattr(profitability, "labor_cost"))
        self.assertFalse(hasattr(profitability, "overhead_cost"))

    # ── 5. old zero/default behavior unchanged ──────────────────────────

    def test_zero_labor_overhead_operation_gives_baseline(self):
        """With all defaults at zero, the commercial pipeline must
        produce the same results as before CI-BS-1/2/3."""
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(
            total_panel_area_m2=10.0,
            total_edge_meters=20.0,
            total_drilling_operations=30,
            total_material_types=4,
        )

        result = self._build_commercial_result(
            context,
            markup_rate=0.25,
        )

        cost = result["cost_report"]
        # Baseline: material 1200 + edge 100 + drilling 45 + complexity 100 = 1445
        self.assertEqual(cost.total_manufacturing_cost, 1445.0)
        self.assertEqual(cost.total_labor_cost, 0.0)
        self.assertEqual(cost.overhead_cost, 0.0)

        quotation = result["quotation_report"]
        self.assertEqual(quotation.production_cost, 1445.0)
        self.assertEqual(quotation.markup_amount, 361.25)  # 1445 * 0.25
        self.assertEqual(quotation.selling_price, 1806.25)

        profitability = result["profitability_report"]
        self.assertEqual(profitability.production_cost, 1445.0)
        self.assertEqual(profitability.gross_profit, 361.25)
        self.assertAlmostEqual(profitability.gross_margin_rate, 0.20, places=2)

    def test_full_pipeline_with_all_improvements(self):
        """The full pipeline with labor + overhead + operation rates
        must produce consistent commercial output."""
        from cost_intelligence.manufacturing_cost_rules import (
            ManufacturingCostRules,
        )

        context = self._make_context(
            total_panel_area_m2=5.0,
            machining_operations_by_type={"DRILL": 10, "ROUTE": 4},
        )
        labor = self._make_labor(
            cnc_labor_cost=50.0,
            drilling_labor_cost=20.0,
            edge_banding_labor_cost=10.0,
            assembly_labor_cost=20.0,
            total_labor_cost=100.0,
        )
        rules = ManufacturingCostRules(
            drilling_rate=1.5,
            operation_rates={"ROUTE": 4.0},
            overhead_flat_cost=150.0,
            overhead_percentage=0.05,
        )

        result = self._build_commercial_result(
            context,
            labor_cost_report=labor,
            rules=rules,
            hardware_cost=40.0,
            markup_rate=0.30,
        )

        cost = result["cost_report"]
        # drill: 10*1.5 = 15 | route: 4*4 = 16 → drilling_cost = 31
        self.assertEqual(cost.drilling_cost, 31.0)
        self.assertEqual(cost.total_labor_cost, 100.0)
        self.assertEqual(cost.hardware_cost, 40.0)
        self.assertEqual(cost.material_cost, 600.0)

        # base = 600 + 31 + 40 + 100 = 771
        base = 600.0 + 31.0 + 40.0 + 100.0
        expected_overhead = 150.0 + (base * 0.05)  # 150 + 38.55 = 188.55
        self.assertEqual(cost.overhead_cost, 188.55)
        self.assertEqual(cost.total_manufacturing_cost, base + 188.55)

        # Commercial layer
        quotation = result["quotation_report"]
        self.assertEqual(quotation.production_cost, base + 188.55)
        self.assertAlmostEqual(
            quotation.selling_price,
            (base + 188.55) * 1.30,
            places=2,
        )

    def test_commercial_pipeline_signature_is_backward_compatible(self):
        """ManufacturingCommercialPipelineBuilder.build() must accept
        the same positional args as before CI-BS-*."""
        from cost_intelligence.manufacturing_commercial_pipeline_builder import (
            ManufacturingCommercialPipelineBuilder,
        )

        import inspect
        sig = inspect.signature(
            ManufacturingCommercialPipelineBuilder.build
        )

        params = list(sig.parameters.keys())
        self.assertIn("manufacturing_production_package", params)
        self.assertIn("markup_rate", params)
        self.assertIn("currency", params)
        self.assertIn("manufacturing_cost_summary", params)
        # No new required params
        self.assertEqual(
            sig.parameters["markup_rate"].default, 0.0
        )

    def test_profitability_report_has_no_cost_component_fields(self):
        """ProfitabilityReport must not expose individual cost
        components — it consumes only production_cost."""
        from dataclasses import fields
        from cost_intelligence.profitability_report import (
            ProfitabilityReport,
        )

        names = [f.name for f in fields(ProfitabilityReport)]
        self.assertIn("production_cost", names)
        self.assertIn("gross_profit", names)
        self.assertIn("gross_margin_rate", names)
        self.assertNotIn("material_cost", names)
        self.assertNotIn("labor_cost", names)
        self.assertNotIn("overhead_cost", names)
        self.assertNotIn("drilling_cost", names)
        self.assertNotIn("machining_cost", names)

    def test_quotation_report_has_no_cost_component_fields(self):
        """QuotationReport must not expose individual cost
        components — it consumes only total_cost."""
        from dataclasses import fields
        from cost_intelligence.quotation_report import (
            QuotationReport,
        )

        names = [f.name for f in fields(QuotationReport)]
        self.assertIn("production_cost", names)
        self.assertNotIn("material_cost", names)
        self.assertNotIn("labor_cost", names)
        self.assertNotIn("overhead_cost", names)


if __name__ == "__main__":
    unittest.main()
