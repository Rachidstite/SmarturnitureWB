import copy
import unittest


class TestManufacturingMetricsBuilder(unittest.TestCase):

    def test_build_aggregates_edge_meters_by_banding_without_mutating_items(self):
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
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )
        from manufacturing.manufacturing_summary_report import (
            ManufacturingSummaryReport,
        )

        edge_items = [
            {"banding": "ABS_1MM", "linear_meters": 1.2},
            {"banding": "PVC_2MM", "linear_meters": 0.8},
            {"banding": "ABS_1MM", "linear_meters": 0.5},
        ]
        original_edge_items = copy.deepcopy(edge_items)
        production_package = ManufacturingProductionPackage(
            cutlist_report=ManufacturingCutlistReport(items=[]),
            edge_report=ManufacturingEdgeReport(
                items=edge_items,
                total_linear_meters=2.5,
            ),
            machining_report=ManufacturingMachiningReport(items=[]),
            summary_report=ManufacturingSummaryReport(total_panels=0),
        )

        report = ManufacturingMetricsBuilder().build(production_package)

        self.assertEqual(
            report.edge_meters_by_banding,
            {
                "ABS_1MM": 1.7,
                "PVC_2MM": 0.8,
            },
        )
        self.assertEqual(report.total_edge_meters, 2.5)
        self.assertEqual(production_package.edge_report.items, original_edge_items)


if __name__ == "__main__":
    unittest.main()
