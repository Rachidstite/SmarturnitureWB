import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingEdgeReportContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from manufacturing.manufacturing_edge_report import (
            ManufacturingEdgeReport,
        )

        self.assertTrue(is_dataclass(ManufacturingEdgeReport))

    def test_contract_has_required_fields(self):
        from manufacturing.manufacturing_edge_report import (
            ManufacturingEdgeReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingEdgeReport)],
            [
                "items",
                "total_items",
                "total_linear_meters",
                "warnings",
            ],
        )

    def test_contract_defaults(self):
        from manufacturing.manufacturing_edge_report import (
            ManufacturingEdgeReport,
        )

        report = ManufacturingEdgeReport()

        self.assertEqual(report.items, [])
        self.assertEqual(report.total_items, 0)
        self.assertEqual(report.total_linear_meters, 0.0)
        self.assertEqual(report.warnings, [])

    def test_list_defaults_are_independent(self):
        from manufacturing.manufacturing_edge_report import (
            ManufacturingEdgeReport,
        )

        first_report = ManufacturingEdgeReport()
        second_report = ManufacturingEdgeReport()

        self.assertIsNot(first_report.items, second_report.items)
        self.assertIsNot(first_report.warnings, second_report.warnings)


if __name__ == "__main__":
    unittest.main()
