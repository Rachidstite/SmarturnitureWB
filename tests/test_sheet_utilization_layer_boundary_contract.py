import inspect
import unittest
from dataclasses import is_dataclass
from types import SimpleNamespace


class TestSheetUtilizationLayerBoundaryContract(unittest.TestCase):

    def test_manufacturing_builder_uses_metrics_style_contract(self):
        from manufacturing.sheet_utilization_builder import (
            SheetUtilizationBuilder as ManufacturingSheetUtilizationBuilder,
        )
        from manufacturing.sheet_utilization_report import (
            SheetUtilizationReport as ManufacturingSheetUtilizationReport,
        )

        metrics_report = SimpleNamespace(
            total_panel_area_m2=10.0,
            warnings=["Metrics warning"],
        )
        snapshot = self._snapshot(metrics_report)

        report = ManufacturingSheetUtilizationBuilder().build(metrics_report)

        self.assertTrue(is_dataclass(report))
        self.assertIsInstance(report, ManufacturingSheetUtilizationReport)
        self.assertEqual(report.total_sheet_area_m2, 11.592)
        self.assertEqual(report.used_area_m2, 10.0)
        self.assertAlmostEqual(report.waste_area_m2, 1.592, places=3)
        self.assertAlmostEqual(report.utilization_percent, (10.0 / 11.592) * 100, places=6)
        self.assertAlmostEqual(report.waste_percent, (1.592 / 11.592) * 100, places=6)
        self.assertEqual(report.warnings, ["Metrics warning"])
        self.assertIsNot(report.warnings, metrics_report.warnings)
        self.assertEqual(self._snapshot(metrics_report), snapshot)

    def test_cost_builder_uses_nesting_style_contract(self):
        from cost_intelligence.sheet_utilization_builder import (
            SheetUtilizationBuilder as CostSheetUtilizationBuilder,
        )
        from cost_intelligence.sheet_utilization_report import (
            SheetUtilizationReport as CostSheetUtilizationReport,
        )

        sheet_results = [
            SimpleNamespace(sheet_width=100, sheet_height=50, used_area=2500),
            SimpleNamespace(sheet_width=200, sheet_height=50, used_area=5000),
        ]
        snapshot = self._snapshot(*sheet_results)

        report = CostSheetUtilizationBuilder().build(sheet_results)

        self.assertTrue(is_dataclass(report))
        self.assertIsInstance(report, CostSheetUtilizationReport)
        self.assertEqual(report.sheet_count, 2)
        self.assertEqual(report.total_sheet_area, 15000)
        self.assertEqual(report.total_used_area, 7500)
        self.assertEqual(report.total_remaining_area, 7500)
        self.assertEqual(report.utilization_rate, 0.5)
        self.assertEqual(report.waste_rate, 0.5)
        self.assertEqual(report.warnings, [])
        self.assertEqual(self._snapshot(*sheet_results), snapshot)

    def test_two_reports_are_different_dataclass_types(self):
        from manufacturing.sheet_utilization_report import (
            SheetUtilizationReport as ManufacturingSheetUtilizationReport,
        )
        from cost_intelligence.sheet_utilization_report import (
            SheetUtilizationReport as CostSheetUtilizationReport,
        )

        self.assertIsNot(ManufacturingSheetUtilizationReport, CostSheetUtilizationReport)
        self.assertTrue(is_dataclass(ManufacturingSheetUtilizationReport))
        self.assertTrue(is_dataclass(CostSheetUtilizationReport))

    def test_builders_do_not_import_each_other(self):
        import manufacturing.sheet_utilization_builder as manufacturing_module
        import cost_intelligence.sheet_utilization_builder as cost_module

        manufacturing_source = inspect.getsource(manufacturing_module)
        cost_source = inspect.getsource(cost_module)

        self.assertNotIn("cost_intelligence.sheet_utilization_builder", manufacturing_source)
        self.assertNotIn("manufacturing.sheet_utilization_builder", cost_source)

    @staticmethod
    def _snapshot(*items):
        return [
            {
                key: list(value) if isinstance(value, list) else value
                for key, value in item.__dict__.items()
            }
            for item in items
        ]


if __name__ == "__main__":
    unittest.main()
