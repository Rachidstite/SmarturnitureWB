import unittest


class TestManufacturingDurationBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.manufacturing_duration_builder import (
            ManufacturingDurationBuilder,
        )

        self.assertTrue(callable(ManufacturingDurationBuilder().build))

    def test_builder_calculates_duration_from_metrics(self):
        from manufacturing.manufacturing_duration_builder import (
            ManufacturingDurationBuilder,
        )
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        report = ManufacturingDurationBuilder().build(
            ManufacturingMetricsReport(
                total_panels=10,
                total_edge_meters=20.0,
                total_drilling_operations=30,
                total_material_types=2,
            )
        )

        self.assertEqual(report.estimated_cnc_minutes, 10.0)
        self.assertEqual(report.estimated_drilling_minutes, 15.0)
        self.assertEqual(report.estimated_edge_banding_minutes, 10.0)
        self.assertEqual(report.estimated_assembly_minutes, 60.0)
        self.assertEqual(report.total_production_minutes, 95.0)

    def test_builder_handles_empty_metrics(self):
        from manufacturing.manufacturing_duration_builder import (
            ManufacturingDurationBuilder,
        )
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        report = ManufacturingDurationBuilder().build(
            ManufacturingMetricsReport()
        )

        self.assertEqual(report.total_production_minutes, 0.0)

    def test_builder_propagates_warnings(self):
        from manufacturing.manufacturing_duration_builder import (
            ManufacturingDurationBuilder,
        )
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        report = ManufacturingDurationBuilder().build(
            ManufacturingMetricsReport(warnings=["Metrics warning"])
        )

        self.assertEqual(report.warnings, ["Metrics warning"])


if __name__ == "__main__":
    unittest.main()
