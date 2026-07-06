"""
OI-BS-2B: Nesting Savings in Factory Dashboard — Contract Tests
=================================================================

Verifies:
- None produces no section / safe fallback
- report values are displayed exactly
- dashboard does not compute deltas
- no forbidden imports
- existing dashboard tests remain green
"""

import importlib
import importlib.machinery
import importlib.util
import sys
import types
import unittest
from types import SimpleNamespace


class TestNestingSavingsDashboardContract(unittest.TestCase):
    """Contract tests for build_nesting_savings_dashboard_section."""

    _mod = None

    @classmethod
    def _load_dashboard(cls):
        if cls._mod is not None:
            return cls._mod

        for key in list(sys.modules):
            if key.startswith("factory_dashboard"):
                del sys.modules[key]

        parent = types.ModuleType("factory_dashboard")
        parent.__path__ = ["factory_dashboard"]
        sys.modules["factory_dashboard"] = parent

        name = "factory_dashboard.dashboard_read_model"
        path = "factory_dashboard/dashboard_read_model.py"
        loader = importlib.machinery.SourceFileLoader(name, path)
        spec = importlib.machinery.ModuleSpec(name, loader, origin=path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        loader.exec_module(mod)
        cls._mod = mod
        return mod

    # ── None → safe fallback ──────────────────────────────────────────

    def test_none_returns_none(self):
        mod = self._load_dashboard()
        result = mod.build_nesting_savings_dashboard_section(None)
        self.assertIsNone(result)

    # ── report values displayed exactly ────────────────────────────────

    def _make_savings_report(self, **overrides):
        from cost_intelligence.nesting_savings_report import NestingSavingsReport
        return NestingSavingsReport(**overrides)

    def test_all_fields_are_displayed(self):
        mod = self._load_dashboard()

        report = self._make_savings_report(
            material_savings=250.0,
            waste_reduction=200.0,
            recovered_value_delta=50.0,
            total_manufacturing_cost_delta=300.0,
            profitability_delta=300.0,
        )

        section = mod.build_nesting_savings_dashboard_section(report)

        self.assertIsNotNone(section)
        self.assertEqual(section.section_name, "Nesting Savings Comparison")
        self.assertEqual(len(section.rows), 5)

        row_map = {label: value for label, value in section.rows}
        self.assertEqual(row_map["Material Savings"], "250.00")
        self.assertEqual(row_map["Waste Reduction"], "200.00")
        self.assertEqual(row_map["Recovered Value Improvement"], "50.00")
        self.assertEqual(row_map["Total Manufacturing Cost Delta"], "300.00")
        self.assertEqual(row_map["Profitability Impact"], "300.00")

    def test_float_precision_two_decimals(self):
        mod = self._load_dashboard()

        report = self._make_savings_report(
            material_savings=123.456,
            waste_reduction=0.0,
            recovered_value_delta=0.001,
            total_manufacturing_cost_delta=999.9999,
            profitability_delta=0.005,
        )

        section = mod.build_nesting_savings_dashboard_section(report)

        row_map = {label: value for label, value in section.rows}
        self.assertEqual(row_map["Material Savings"], "123.46")
        self.assertEqual(row_map["Waste Reduction"], "0.00")
        self.assertEqual(row_map["Recovered Value Improvement"], "0.00")
        self.assertEqual(row_map["Total Manufacturing Cost Delta"], "1000.00")
        self.assertEqual(row_map["Profitability Impact"], "0.01")

    def test_negative_values_display_correctly(self):
        mod = self._load_dashboard()

        report = self._make_savings_report(
            material_savings=-100.0,
            total_manufacturing_cost_delta=-150.0,
            profitability_delta=-150.0,
        )

        section = mod.build_nesting_savings_dashboard_section(report)

        row_map = {label: value for label, value in section.rows}
        self.assertEqual(row_map["Material Savings"], "-100.00")
        self.assertEqual(row_map["Total Manufacturing Cost Delta"], "-150.00")
        self.assertEqual(row_map["Profitability Impact"], "-150.00")

    def test_zero_report_produces_section_with_all_zeros(self):
        mod = self._load_dashboard()

        report = self._make_savings_report()
        section = mod.build_nesting_savings_dashboard_section(report)

        self.assertIsNotNone(section)
        for label, value in section.rows:
            self.assertEqual(value, "0.00")

    def test_accepts_any_object_with_required_fields(self):
        mod = self._load_dashboard()

        report = SimpleNamespace(
            material_savings=50.0,
            waste_reduction=30.0,
            recovered_value_delta=10.0,
            total_manufacturing_cost_delta=70.0,
            profitability_delta=70.0,
        )

        section = mod.build_nesting_savings_dashboard_section(report)

        self.assertIsNotNone(section)
        row_map = {label: value for label, value in section.rows}
        self.assertEqual(row_map["Material Savings"], "50.00")
        self.assertEqual(row_map["Total Manufacturing Cost Delta"], "70.00")

    # ── dashboard does not compute deltas ─────────────────────────────

    def test_section_builder_does_not_import_cost_calculator(self):
        import inspect
        from factory_dashboard.dashboard_read_model import (
            build_nesting_savings_dashboard_section,
        )
        source = inspect.getsource(build_nesting_savings_dashboard_section)
        self.assertNotIn("from cost_intelligence", source)
        self.assertNotIn("import ManufacturingCostCalculator", source)
        self.assertNotIn("import ManufacturingCostReport", source)
        self.assertNotIn("NestingSavingsBuilder", source)

    def test_section_builder_does_not_import_optimization_internals(self):
        import inspect
        from factory_dashboard.dashboard_read_model import (
            build_nesting_savings_dashboard_section,
        )
        source = inspect.getsource(build_nesting_savings_dashboard_section)
        self.assertNotIn("NestingSavingsBuilder", source)
        self.assertNotIn("optimization", source.lower())

    def test_section_builder_no_ui_or_scene_renderer(self):
        import inspect
        from factory_dashboard.dashboard_read_model import (
            build_nesting_savings_dashboard_section,
        )
        source = inspect.getsource(build_nesting_savings_dashboard_section)
        self.assertNotIn("SceneRenderer", source)
        self.assertNotIn("PySide", source)
        self.assertNotIn("Qt", source)

    def test_section_builder_no_cost_computation(self):
        import inspect
        from factory_dashboard.dashboard_read_model import (
            build_nesting_savings_dashboard_section,
        )
        source = inspect.getsource(build_nesting_savings_dashboard_section)
        self.assertNotIn("calculate", source)
        self.assertNotIn("Calculator", source)


if __name__ == "__main__":
    unittest.main()
