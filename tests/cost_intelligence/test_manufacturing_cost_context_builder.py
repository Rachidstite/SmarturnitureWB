import unittest


class TestManufacturingCostContextBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.manufacturing_cost_context_builder import (
            ManufacturingCostContextBuilder,
        )

        self.assertTrue(callable(ManufacturingCostContextBuilder().build))

    def test_build_preserves_metrics_report_exactly(self):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )
        from cost_intelligence.manufacturing_cost_context_builder import (
            ManufacturingCostContextBuilder,
        )
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        warnings = ["Missing edge data"]
        metrics_report = ManufacturingMetricsReport(
            total_panels=4,
            total_panel_area_m2=3.25,
            total_edge_meters=6.5,
            total_drilling_operations=12,
            total_material_types=2,
            warnings_count=1,
            warnings=warnings,
        )

        context = ManufacturingCostContextBuilder().build(metrics_report)

        self.assertIsInstance(context, ManufacturingCostContext)
        self.assertEqual(context.total_panels, metrics_report.total_panels)
        self.assertEqual(
            context.total_panel_area_m2,
            metrics_report.total_panel_area_m2,
        )
        self.assertEqual(
            context.total_edge_meters,
            metrics_report.total_edge_meters,
        )
        self.assertEqual(
            context.total_drilling_operations,
            metrics_report.total_drilling_operations,
        )
        self.assertEqual(
            context.total_material_types,
            metrics_report.total_material_types,
        )
        self.assertEqual(context.warnings_count, metrics_report.warnings_count)
        self.assertIs(context.warnings, metrics_report.warnings)


if __name__ == "__main__":
    unittest.main()
