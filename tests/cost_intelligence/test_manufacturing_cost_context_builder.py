import unittest
import copy


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
        edge_meters_by_banding = {
            "ABS_1MM": 4.0,
            "PVC_2MM": 2.5,
        }
        machining_operations_by_type = {
            "DRILL": 12,
            "ROUTE": 2,
        }
        original_edge_meters_by_banding = copy.deepcopy(edge_meters_by_banding)
        original_machining_operations_by_type = copy.deepcopy(
            machining_operations_by_type
        )
        metrics_report = ManufacturingMetricsReport(
            total_panels=4,
            total_panel_area_m2=3.25,
            total_edge_meters=6.5,
            edge_meters_by_banding=edge_meters_by_banding,
            total_drilling_operations=12,
            machining_operations_by_type=machining_operations_by_type,
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
        self.assertIs(
            context.edge_meters_by_banding,
            metrics_report.edge_meters_by_banding,
        )
        self.assertEqual(
            context.total_drilling_operations,
            metrics_report.total_drilling_operations,
        )
        self.assertIs(
            context.machining_operations_by_type,
            metrics_report.machining_operations_by_type,
        )
        self.assertEqual(
            context.total_material_types,
            metrics_report.total_material_types,
        )
        self.assertEqual(context.warnings_count, metrics_report.warnings_count)
        self.assertIs(context.warnings, metrics_report.warnings)
        self.assertEqual(
            metrics_report.edge_meters_by_banding,
            original_edge_meters_by_banding,
        )
        self.assertEqual(
            metrics_report.machining_operations_by_type,
            original_machining_operations_by_type,
        )


if __name__ == "__main__":
    unittest.main()
