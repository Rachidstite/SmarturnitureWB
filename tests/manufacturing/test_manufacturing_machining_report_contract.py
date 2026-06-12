import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingMachiningReportContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from manufacturing.manufacturing_machining_report import (
            ManufacturingMachiningReport,
        )

        self.assertTrue(is_dataclass(ManufacturingMachiningReport))

    def test_contract_has_required_fields(self):
        from manufacturing.manufacturing_machining_report import (
            ManufacturingMachiningReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingMachiningReport)],
            ["items", "total_items", "warnings"],
        )

    def test_contract_defaults(self):
        from manufacturing.manufacturing_machining_report import (
            ManufacturingMachiningReport,
        )

        report = ManufacturingMachiningReport()

        self.assertEqual(report.items, [])
        self.assertEqual(report.total_items, 0)
        self.assertEqual(report.warnings, [])

    def test_list_defaults_are_independent(self):
        from manufacturing.manufacturing_machining_report import (
            ManufacturingMachiningReport,
        )

        first_report = ManufacturingMachiningReport()
        second_report = ManufacturingMachiningReport()

        self.assertIsNot(first_report.items, second_report.items)
        self.assertIsNot(first_report.warnings, second_report.warnings)


if __name__ == "__main__":
    unittest.main()
