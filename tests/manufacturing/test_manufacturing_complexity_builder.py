import unittest


class TestManufacturingComplexityBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.manufacturing_complexity_builder import (
            ManufacturingComplexityBuilder,
        )

        self.assertTrue(callable(ManufacturingComplexityBuilder().build))

    def test_low_complexity_for_small_simple_project(self):
        from manufacturing.manufacturing_complexity_builder import (
            ManufacturingComplexityBuilder,
        )
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        report = ManufacturingComplexityBuilder().build(
            ManufacturingMetricsReport(
                total_panels=4,
                total_edge_meters=10.0,
                total_drilling_operations=8,
                total_material_types=1,
            )
        )

        self.assertEqual(report.complexity_level, "LOW")
        self.assertLess(report.complexity_score, 40)

    def test_high_complexity_for_large_heavy_project(self):
        from manufacturing.manufacturing_complexity_builder import (
            ManufacturingComplexityBuilder,
        )
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        report = ManufacturingComplexityBuilder().build(
            ManufacturingMetricsReport(
                total_panels=80,
                total_edge_meters=180.0,
                total_drilling_operations=260,
                total_material_types=5,
            )
        )

        self.assertEqual(report.complexity_level, "HIGH")
        self.assertGreaterEqual(report.complexity_score, 70)
        self.assertIn("High panel count", report.main_drivers)
        self.assertIn("High drilling complexity", report.main_drivers)
        self.assertIn("High edge banding workload", report.main_drivers)
        self.assertIn("Multiple material types", report.main_drivers)

    def test_medium_complexity_for_moderate_project(self):
        from manufacturing.manufacturing_complexity_builder import (
            ManufacturingComplexityBuilder,
        )
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        report = ManufacturingComplexityBuilder().build(
            ManufacturingMetricsReport(
                total_panels=25,
                total_edge_meters=60.0,
                total_drilling_operations=80,
                total_material_types=2,
            )
        )

        self.assertEqual(report.complexity_level, "MEDIUM")
        self.assertGreaterEqual(report.complexity_score, 40)
        self.assertLess(report.complexity_score, 70)

    def test_builder_propagates_warnings(self):
        from manufacturing.manufacturing_complexity_builder import (
            ManufacturingComplexityBuilder,
        )
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        report = ManufacturingComplexityBuilder().build(
            ManufacturingMetricsReport(warnings=["Metrics warning"])
        )

        self.assertEqual(report.warnings, ["Metrics warning"])


if __name__ == "__main__":
    unittest.main()
