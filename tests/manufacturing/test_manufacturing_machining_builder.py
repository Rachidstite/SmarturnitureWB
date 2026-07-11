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

    def test_build_preserves_identity_metadata_for_downstream_consumers(self):
        from manufacturing.manufacturing_machining_builder import (
            ManufacturingMachiningBuilder,
        )
        from manufacturing.manufacturing_package import ManufacturingPackage
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )

        operation = UnifiedManufacturingOperation(
            operation_type="DRILL",
            diameter=5.0,
            depth=12.0,
            face="LEFT",
            axis="Z",
            source="door-01::hinge-1",
            metadata={
                "panel_identity": "door-01",
                "component_reference": "door-01",
                "cabinet_reference": "cabinet-01",
                "source_operation_reference": "door-01::hinge-1",
                "hardware_intent": "INTENT_HINGE",
            },
        )
        package = ManufacturingPackage(machining_operations=[operation])

        report = ManufacturingMachiningBuilder().build(package)

        self.assertEqual(
            report.items[0]["panel_identity"],
            "door-01",
        )
        self.assertEqual(
            report.items[0]["source_operation_reference"],
            "door-01::hinge-1",
        )
        self.assertEqual(
            report.items[0]["component_reference"],
            "door-01",
        )
        self.assertEqual(
            report.items[0]["cabinet_reference"],
            "cabinet-01",
        )
        self.assertEqual(
            report.items[0]["hardware_intent"],
            "INTENT_HINGE",
        )


if __name__ == "__main__":
    unittest.main()
