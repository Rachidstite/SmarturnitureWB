import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingMetricsReportContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        self.assertTrue(is_dataclass(ManufacturingMetricsReport))

    def test_contract_has_required_fields_in_order(self):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingMetricsReport)],
            [
                "total_panels",
                "total_panel_area_m2",
                "total_edge_meters",
                "edge_meters_by_banding",
                "total_drilling_operations",
                "machining_operations_by_type",
                "total_material_types",
                "warnings_count",
                "warnings",
            ],
        )

    def test_edge_meters_by_banding_defaults_to_empty_independent_dict(self):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        first_report = ManufacturingMetricsReport()
        second_report = ManufacturingMetricsReport()

        self.assertEqual(first_report.edge_meters_by_banding, {})
        self.assertIsNot(
            first_report.edge_meters_by_banding,
            second_report.edge_meters_by_banding,
        )

    def test_machining_operations_by_type_defaults_to_empty_independent_dict(self):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        first_report = ManufacturingMetricsReport()
        second_report = ManufacturingMetricsReport()

        self.assertEqual(first_report.machining_operations_by_type, {})
        self.assertIsNot(
            first_report.machining_operations_by_type,
            second_report.machining_operations_by_type,
        )


if __name__ == "__main__":
    unittest.main()
