import unittest


class TestSheetUtilizationBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.sheet_utilization_builder import (
            SheetUtilizationBuilder,
        )

        self.assertTrue(callable(SheetUtilizationBuilder().build))

    def test_builder_calculates_utilization_from_metrics_report(self):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )
        from manufacturing.sheet_utilization_builder import (
            SheetUtilizationBuilder,
        )

        report = SheetUtilizationBuilder().build(
            ManufacturingMetricsReport(
                total_panel_area_m2=10.0,
                warnings=["Metrics warning"],
            )
        )

        self.assertEqual(report.total_sheet_area_m2, 11.592)
        self.assertEqual(report.used_area_m2, 10.0)
        self.assertAlmostEqual(report.waste_area_m2, 1.592, places=3)
        self.assertAlmostEqual(
            report.utilization_percent,
            (10.0 / 11.592) * 100,
            places=6,
        )
        self.assertAlmostEqual(
            report.waste_percent,
            (1.592 / 11.592) * 100,
            places=6,
        )
        self.assertEqual(report.warnings, ["Metrics warning"])

    def test_builder_returns_zeros_when_no_panel_area(self):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )
        from manufacturing.sheet_utilization_builder import (
            SheetUtilizationBuilder,
        )

        report = SheetUtilizationBuilder().build(ManufacturingMetricsReport())

        self.assertEqual(report.total_sheet_area_m2, 0.0)
        self.assertEqual(report.used_area_m2, 0.0)
        self.assertEqual(report.waste_area_m2, 0.0)
        self.assertEqual(report.utilization_percent, 0.0)
        self.assertEqual(report.waste_percent, 0.0)

    def test_builder_propagates_warnings_without_mutating_metrics_report(self):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )
        from manufacturing.sheet_utilization_builder import (
            SheetUtilizationBuilder,
        )

        metrics_report = ManufacturingMetricsReport(
            total_panel_area_m2=5.0,
            warnings=["Metrics warning"],
        )

        report = SheetUtilizationBuilder().build(metrics_report)

        self.assertEqual(report.warnings, ["Metrics warning"])
        self.assertEqual(metrics_report.warnings, ["Metrics warning"])
        self.assertIsNot(report.warnings, metrics_report.warnings)


if __name__ == "__main__":
    unittest.main()
