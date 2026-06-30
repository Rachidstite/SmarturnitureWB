import unittest


class TestManufacturingProductionPackageBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.manufacturing_production_package_builder import (
            ManufacturingProductionPackageBuilder,
        )

        self.builder = ManufacturingProductionPackageBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_valid_package_builds_ready_production_package(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        production_package = self.builder.build(self._valid_package())

        self.assertIsInstance(
            production_package,
            ManufacturingProductionPackage,
        )
        self.assertIsNotNone(production_package.cutlist_report)
        self.assertIsNotNone(production_package.edge_report)
        self.assertIsNotNone(production_package.machining_report)
        self.assertIsNotNone(production_package.summary_report)
        self.assertTrue(production_package.release_ready)
        self.assertEqual(
            production_package.warnings,
            [
                "Door panels present but hinge hardware evidence is missing.",
            ],
        )

    def test_empty_package_builds_blocked_production_package(self):
        from manufacturing.manufacturing_package import ManufacturingPackage

        production_package = self.builder.build(ManufacturingPackage())

        self.assertIsNotNone(production_package.cutlist_report)
        self.assertIsNotNone(production_package.edge_report)
        self.assertIsNotNone(production_package.machining_report)
        self.assertIsNotNone(production_package.summary_report)
        self.assertFalse(production_package.release_ready)
        self.assertEqual(
            production_package.warnings,
            [
                "No panels",
                "No materials",
                "No machining operations",
                "No edge operations",
            ],
        )

    @staticmethod
    def _valid_package():
        from manufacturing.edge_spec import EdgeSpec
        from manufacturing.manufacturing_package import ManufacturingPackage
        from manufacturing.material_spec import MaterialSpec
        from manufacturing.panel_spec import PanelSpec
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )
        from shared.roles import NodeRole

        return ManufacturingPackage(
            panels=[
                PanelSpec(
                    identity="door-01",
                    role=NodeRole.DOOR_PANEL,
                    width=600.0,
                    height=720.0,
                    thickness=18.0,
                    material="MDF_18MM",
                    edge_spec=EdgeSpec(top="ABS_1MM"),
                )
            ],
            materials=[MaterialSpec(name="MDF_18MM", thickness=18.0)],
            machining_operations=[
                UnifiedManufacturingOperation(operation_type="DRILL")
            ],
            edge_operations=[
                UnifiedManufacturingOperation(operation_type="EDGE_BANDING")
            ],
        )


if __name__ == "__main__":
    unittest.main()
