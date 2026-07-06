"""
CI-BS-1: Wire Labor Costs into Manufacturing Cost Pipeline
==========================================================

Contract tests proving:
  - labor cost reaches ManufacturingCostReport
  - zero labor still works
  - existing cost calculations remain unchanged
  - backward compatibility preserved
"""

import inspect
import unittest
from dataclasses import fields
from types import SimpleNamespace


class TestLaborCostPipelineContract(unittest.TestCase):
    """Contract tests for labor cost integration into the manufacturing cost pipeline."""

    # ── helpers ──────────────────────────────────────────────────────────

    def _make_context(self, **overrides):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        return ManufacturingCostContext(**overrides)

    def _make_labor_report(self, **overrides):
        from manufacturing.labor_cost_report import LaborCostReport

        return LaborCostReport(**overrides)

    def _make_duration_report(self, **overrides):
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        return ManufacturingDurationReport(**overrides)

    # ── 1. labor cost reaches ManufacturingCostReport ────────────────────

    def test_labor_cost_fields_exist_on_manufacturing_cost_report(self):
        """ManufacturingCostReport must expose all 5 labor cost fields."""
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        names = [f.name for f in fields(ManufacturingCostReport)]

        self.assertIn("cnc_labor_cost", names)
        self.assertIn("drilling_labor_cost", names)
        self.assertIn("edge_banding_labor_cost", names)
        self.assertIn("assembly_labor_cost", names)
        self.assertIn("total_labor_cost", names)

    def test_calculator_populates_labor_fields_from_labor_cost_report(self):
        """ManufacturingCostCalculator.calculate() must populate labor
        fields from an optional labor_cost_report."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        context = ManufacturingCostContext(total_panels=2)
        labor = self._make_labor_report(
            cnc_labor_cost=50.0,
            drilling_labor_cost=30.0,
            edge_banding_labor_cost=20.0,
            assembly_labor_cost=100.0,
            total_labor_cost=200.0,
        )

        report = ManufacturingCostCalculator().calculate(
            context, labor_cost_report=labor
        )

        self.assertEqual(report.cnc_labor_cost, 50.0)
        self.assertEqual(report.drilling_labor_cost, 30.0)
        self.assertEqual(report.edge_banding_labor_cost, 20.0)
        self.assertEqual(report.assembly_labor_cost, 100.0)
        self.assertEqual(report.total_labor_cost, 200.0)

    def test_total_manufacturing_cost_includes_labor_cost(self):
        """total_manufacturing_cost must include total_labor_cost in its sum."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        context = ManufacturingCostContext(
            total_panel_area_m2=10.0,
            total_edge_meters=20.0,
            total_drilling_operations=30,
            total_material_types=4,
        )
        labor = self._make_labor_report(total_labor_cost=200.0)

        report = ManufacturingCostCalculator().calculate(
            context, labor_cost_report=labor
        )

        expected_non_labor = (
            report.material_cost
            + report.edge_banding_cost
            + report.drilling_cost
            + report.hardware_cost
            + report.complexity_cost
            + report.panel_handling_cost
        )
        self.assertEqual(
            report.total_manufacturing_cost,
            expected_non_labor + 200.0,
        )

    def test_pipeline_builder_forwards_labor_cost_report_to_calculator(self):
        """ManufacturingCostPipelineBuilder must build a LaborCostReport
        and pass it to the calculator."""
        from cost_intelligence.manufacturing_cost_pipeline_builder import (
            ManufacturingCostPipelineBuilder,
        )

        source = inspect.getsource(
            __import__(
                "cost_intelligence.manufacturing_cost_pipeline_builder",
                fromlist=["ManufacturingCostPipelineBuilder"],
            )
        )

        self.assertIn("LaborCostBuilder", source)
        self.assertIn("labor_cost_report", source)
        self.assertIn("ManufacturingDurationBuilder", source)

    # ── 2. zero labor still works ────────────────────────────────────────

    def test_zero_labor_cost_report_produces_zero_labor_fields(self):
        """Passing a zero-valued LaborCostReport must produce zero labor fields."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        context = ManufacturingCostContext(total_panel_area_m2=10.0)
        zero_labor = self._make_labor_report()

        report = ManufacturingCostCalculator().calculate(
            context, labor_cost_report=zero_labor
        )

        self.assertEqual(report.cnc_labor_cost, 0.0)
        self.assertEqual(report.drilling_labor_cost, 0.0)
        self.assertEqual(report.edge_banding_labor_cost, 0.0)
        self.assertEqual(report.assembly_labor_cost, 0.0)
        self.assertEqual(report.total_labor_cost, 0.0)

    def test_pipeline_builder_with_zero_rates_produces_zero_labor(self):
        """Calling ManufacturingCostPipelineBuilder without rates yields
        zero labor costs."""
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
                        "width": 100.0,
                        "height": 200.0,
                        "thickness": 18.0,
                        "material": "MDF",
                        "quantity": 1,
                    }
                ],
                total_items=1,
                warnings=[],
            ),
            edge_report=ManufacturingEdgeReport(
                items=[],
                total_items=0,
                total_linear_meters=0.0,
                warnings=[],
            ),
            machining_report=ManufacturingMachiningReport(
                items=[],
                total_items=0,
                warnings=[],
            ),
            summary_report=ManufacturingSummaryReport(
                total_panels=1,
                total_materials=1,
                total_edge_operations=0,
                total_machining_operations=0,
                warnings=[],
            ),
            warnings=[],
        )

        summary = ManufacturingCostPipelineBuilder().build(package)

        self.assertEqual(summary.cost_report.cnc_labor_cost, 0.0)
        self.assertEqual(summary.cost_report.drilling_labor_cost, 0.0)
        self.assertEqual(summary.cost_report.edge_banding_labor_cost, 0.0)
        self.assertEqual(summary.cost_report.assembly_labor_cost, 0.0)
        self.assertEqual(summary.cost_report.total_labor_cost, 0.0)

    # ── 3. existing cost calculations remain unchanged ───────────────────

    def test_existing_costs_preserved_when_labor_added(self):
        """material_cost, edge_banding_cost, drilling_cost, hardware_cost,
        complexity_cost, panel_handling_cost must remain unchanged when
        labor is added."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        context = ManufacturingCostContext(
            total_panel_area_m2=10.0,
            total_edge_meters=20.0,
            total_drilling_operations=30,
            total_material_types=4,
            total_panels=5,
        )

        report_no_labor = ManufacturingCostCalculator().calculate(context)
        labor = self._make_labor_report(total_labor_cost=200.0)
        report_with_labor = ManufacturingCostCalculator().calculate(
            context, labor_cost_report=labor
        )

        self.assertEqual(
            report_with_labor.material_cost, report_no_labor.material_cost
        )
        self.assertEqual(
            report_with_labor.edge_banding_cost, report_no_labor.edge_banding_cost
        )
        self.assertEqual(
            report_with_labor.drilling_cost, report_no_labor.drilling_cost
        )
        self.assertEqual(
            report_with_labor.hardware_cost, report_no_labor.hardware_cost
        )
        self.assertEqual(
            report_with_labor.complexity_cost, report_no_labor.complexity_cost
        )
        self.assertEqual(
            report_with_labor.panel_handling_cost,
            report_no_labor.panel_handling_cost,
        )

    def test_pipeline_builder_preserves_existing_cost_breakdown(self):
        """The pipeline builder must preserve material/edge/drilling/hardware
        costs exactly as before."""
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
                items=[
                    {
                        "panel_identity": "panel-01",
                        "edge": "TOP",
                        "banding": "ABS_1MM",
                        "linear_meters": 0.6,
                    }
                ],
                total_items=1,
                total_linear_meters=0.6,
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
                    }
                ],
                total_items=1,
                warnings=[],
            ),
            summary_report=ManufacturingSummaryReport(
                total_panels=2,
                total_materials=1,
                total_edge_operations=1,
                total_machining_operations=1,
                warnings=[],
            ),
            warnings=[],
        )

        summary = ManufacturingCostPipelineBuilder().build(package)

        cost = summary.cost_report
        self.assertGreater(cost.material_cost, 0.0)
        self.assertGreater(cost.edge_banding_cost, 0.0)
        self.assertGreater(cost.drilling_cost, 0.0)
        self.assertEqual(cost.hardware_cost, 0.0)

    # ── 4. backward compatibility preserved ─────────────────────────────

    def test_calculate_without_labor_cost_report_still_works(self):
        """Calling calculate() without labor_cost_report (backward
        compatible path) must still produce a valid report with defaults."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        context = self._make_context(
            total_panel_area_m2=5.0,
            total_edge_meters=10.0,
            total_drilling_operations=10,
        )

        report = ManufacturingCostCalculator().calculate(context)

        self.assertEqual(report.cnc_labor_cost, 0.0)
        self.assertEqual(report.total_labor_cost, 0.0)
        self.assertGreater(report.total_manufacturing_cost, 0.0)

    def test_calculate_with_explicit_none_labor_cost_report_is_safe(self):
        """Passing labor_cost_report=None explicitly must behave the same
        as omitting it."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        context = self._make_context(
            total_panel_area_m2=5.0,
            total_edge_meters=10.0,
            total_drilling_operations=10,
        )

        report = ManufacturingCostCalculator().calculate(
            context, labor_cost_report=None
        )

        self.assertEqual(report.cnc_labor_cost, 0.0)
        self.assertEqual(report.total_labor_cost, 0.0)
        self.assertGreater(report.total_manufacturing_cost, 0.0)

    def test_labor_cost_report_signature_is_optional(self):
        """The calculate() method signature must still accept
        labor_cost_report as an optional keyword argument."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )

        sig = inspect.signature(ManufacturingCostCalculator.calculate)

        self.assertIn("labor_cost_report", sig.parameters)
        self.assertEqual(
            sig.parameters["labor_cost_report"].default,
            None,
        )

    def test_pipeline_builder_signature_accepts_hourly_rates_as_optional(self):
        """The pipeline builder build() method must accept hourly rates
        as optional keyword arguments with defaults of 0.0."""
        from cost_intelligence.manufacturing_cost_pipeline_builder import (
            ManufacturingCostPipelineBuilder,
        )

        sig = inspect.signature(ManufacturingCostPipelineBuilder.build)

        for param in [
            "cnc_hourly_rate",
            "drilling_hourly_rate",
            "edge_banding_hourly_rate",
            "assembly_hourly_rate",
        ]:
            self.assertIn(param, sig.parameters)
            self.assertEqual(sig.parameters[param].default, 0.0)

    def test_labor_warnings_merge_with_context_warnings(self):
        """When labor_cost_report has warnings, they must be merged with
        context warnings in the final ManufacturingCostReport."""
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        context = ManufacturingCostContext(
            warnings=["Context warning A"],
        )
        labor = self._make_labor_report(
            total_labor_cost=100.0,
            warnings=["Labor rate is defaulting to zero"],
        )

        report = ManufacturingCostCalculator().calculate(
            context, labor_cost_report=labor
        )

        self.assertIn("Context warning A", report.warnings)
        self.assertIn("Labor rate is defaulting to zero", report.warnings)


if __name__ == "__main__":
    unittest.main()
