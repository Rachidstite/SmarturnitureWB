import unittest


class TestManufacturingMetricsBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.manufacturing_metrics_builder import (
            ManufacturingMetricsBuilder,
        )

        self.assertTrue(callable(ManufacturingMetricsBuilder().build))

    def test_build_returns_metrics_from_production_package(self):
        from manufacturing.manufacturing_cutlist_report import (
            ManufacturingCutlistReport,
        )
        from manufacturing.manufacturing_edge_report import (
            ManufacturingEdgeReport,
        )
        from manufacturing.manufacturing_machining_report import (
            ManufacturingMachiningReport,
        )
        from manufacturing.manufacturing_metrics_builder import (
            ManufacturingMetricsBuilder,
        )
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )
        from manufacturing.manufacturing_summary_report import (
            ManufacturingSummaryReport,
        )

        warnings = ["Missing edge data"]
        production_package = ManufacturingProductionPackage(
            cutlist_report=ManufacturingCutlistReport(
                items=[
                    {
                        "width": 600.0,
                        "height": 720.0,
                        "quantity": 2,
                        "material": "MDF_18MM",
                    },
                    {
                        "width": 500.0,
                        "height": 400.0,
                        "quantity": 1,
                        "material": "MDF_18MM",
                    },
                    {
                        "width": 1000.0,
                        "height": 300.0,
                        "quantity": 1,
                        "material": "HDF_3MM",
                    },
                ]
            ),
            edge_report=ManufacturingEdgeReport(total_linear_meters=3.25),
            machining_report=ManufacturingMachiningReport(
                items=[
                    {"operation_type": "DRILL"},
                    {"operation_type": "ROUTE"},
                    {"operation_type": "DRILL"},
                ]
            ),
            summary_report=ManufacturingSummaryReport(total_panels=3),
            warnings=warnings,
        )

        report = ManufacturingMetricsBuilder().build(production_package)

        self.assertIsInstance(report, ManufacturingMetricsReport)
        self.assertEqual(report.total_panels, 3)
        self.assertEqual(report.total_panel_area_m2, 1.364)
        self.assertEqual(report.total_edge_meters, 3.25)
        self.assertEqual(report.total_drilling_operations, 2)
        self.assertEqual(report.total_material_types, 2)
        self.assertEqual(report.warnings_count, 1)
        self.assertIs(report.warnings, warnings)


if __name__ == "__main__":
    unittest.main()
