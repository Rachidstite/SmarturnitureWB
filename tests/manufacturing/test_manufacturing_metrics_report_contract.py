import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingMetricsReportContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        self.assertTrue(is_dataclass(ManufacturingMetricsReport))

    def test_contract_has_required_fields(self):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingMetricsReport)],
            [
                "total_panels",
                "total_panel_area_m2",
                "total_edge_meters",
                "total_drilling_operations",
                "total_material_types",
                "warnings_count",
                "warnings",
            ],
        )

    def test_contract_defaults(self):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        report = ManufacturingMetricsReport()

        self.assertEqual(report.total_panels, 0)
        self.assertEqual(report.total_panel_area_m2, 0.0)
        self.assertEqual(report.total_edge_meters, 0.0)
        self.assertEqual(report.total_drilling_operations, 0)
        self.assertEqual(report.total_material_types, 0)
        self.assertEqual(report.warnings_count, 0)
        self.assertEqual(report.warnings, [])

    def test_warning_defaults_are_independent(self):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        first_report = ManufacturingMetricsReport()
        second_report = ManufacturingMetricsReport()

        self.assertIsNot(first_report.warnings, second_report.warnings)


if __name__ == "__main__":
    unittest.main()
