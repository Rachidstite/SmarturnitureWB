import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingProductionPackageContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        self.assertTrue(is_dataclass(ManufacturingProductionPackage))

    def test_contract_has_required_fields(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingProductionPackage)],
            [
                "cutlist_report",
                "edge_report",
                "machining_report",
                "summary_report",
                "release_ready",
                "warnings",
            ],
        )

    def test_contract_defaults(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        package = ManufacturingProductionPackage()

        self.assertIsNone(package.cutlist_report)
        self.assertIsNone(package.edge_report)
        self.assertIsNone(package.machining_report)
        self.assertIsNone(package.summary_report)
        self.assertFalse(package.release_ready)
        self.assertEqual(package.warnings, [])

    def test_warning_defaults_are_independent(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        first_package = ManufacturingProductionPackage()
        second_package = ManufacturingProductionPackage()

        first_package.warnings.append("warning")

        self.assertEqual(second_package.warnings, [])
        self.assertIsNot(first_package.warnings, second_package.warnings)


if __name__ == "__main__":
    unittest.main()
