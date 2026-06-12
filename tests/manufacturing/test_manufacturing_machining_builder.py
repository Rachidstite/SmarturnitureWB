import unittest


class TestManufacturingMachiningBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.manufacturing_machining_builder import (
            ManufacturingMachiningBuilder,
        )

        self.assertTrue(callable(ManufacturingMachiningBuilder().build))

    def test_build_returns_machining_report_for_package_operations(self):
        from manufacturing.manufacturing_machining_builder import (
            ManufacturingMachiningBuilder,
        )
        from manufacturing.manufacturing_machining_report import (
            ManufacturingMachiningReport,
        )
        from manufacturing.manufacturing_package import ManufacturingPackage
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )

        operation = UnifiedManufacturingOperation(
            operation_type="DRILL",
            diameter=5.0,
            depth=12.0,
            is_through=False,
            x=100.0,
            y=200.0,
            z=0.0,
            face="TOP",
            axis="Z",
            source="panel-01",
        )
        package = ManufacturingPackage(
            machining_operations=[operation],
            warnings=["Missing edge data"],
        )

        report = ManufacturingMachiningBuilder().build(package)

        self.assertIsInstance(report, ManufacturingMachiningReport)
        self.assertEqual(
            report.items,
            [
                {
                    "operation_type": "DRILL",
                    "diameter": 5.0,
                    "depth": 12.0,
                    "is_through": False,
                    "x": 100.0,
                    "y": 200.0,
                    "z": 0.0,
                    "face": "TOP",
                    "axis": "Z",
                    "source": "panel-01",
                }
            ],
        )
        self.assertEqual(report.total_items, 1)
        self.assertIs(report.warnings, package.warnings)


if __name__ == "__main__":
    unittest.main()
