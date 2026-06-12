import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingCutlistReportContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from manufacturing.manufacturing_cutlist_report import (
            ManufacturingCutlistReport,
        )

        self.assertTrue(is_dataclass(ManufacturingCutlistReport))

    def test_contract_has_required_fields(self):
        from manufacturing.manufacturing_cutlist_report import (
            ManufacturingCutlistReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingCutlistReport)],
            ["items", "total_items", "warnings"],
        )

    def test_contract_defaults(self):
        from manufacturing.manufacturing_cutlist_report import (
            ManufacturingCutlistReport,
        )

        report = ManufacturingCutlistReport()

        self.assertEqual(report.items, [])
        self.assertEqual(report.total_items, 0)
        self.assertEqual(report.warnings, [])

    def test_list_defaults_are_independent(self):
        from manufacturing.manufacturing_cutlist_report import (
            ManufacturingCutlistReport,
        )

        first_report = ManufacturingCutlistReport()
        second_report = ManufacturingCutlistReport()

        self.assertIsNot(first_report.items, second_report.items)
        self.assertIsNot(first_report.warnings, second_report.warnings)


if __name__ == "__main__":
    unittest.main()
