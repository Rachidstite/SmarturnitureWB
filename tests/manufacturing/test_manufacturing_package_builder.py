import unittest


class TestManufacturingPackageBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.manufacturing_package_builder import (
            ManufacturingPackageBuilder,
        )

        self.builder = ManufacturingPackageBuilder()

    def test_build_accepts_existing_manufacturing_outputs(self):
        from manufacturing.material_spec import MaterialSpec
        from manufacturing.panel_spec import PanelSpec
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )
        from shared.roles import NodeRole

        panels = [
            PanelSpec(
                identity="side-left",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=18.0,
                material="MDF_18MM",
            )
        ]
        materials = [MaterialSpec(name="MDF_18MM", thickness=18.0)]
        edge_operations = [
            UnifiedManufacturingOperation(operation_type="EDGE_BANDING")
        ]
        machining_operations = [
            UnifiedManufacturingOperation(operation_type="DRILL", diameter=5.0)
        ]
        warnings = ["Missing grain direction"]

        package = self.builder.build(
            panels=panels,
            materials=materials,
            edge_operations=edge_operations,
            machining_operations=machining_operations,
            warnings=warnings,
        )

        self.assertIs(package.panels, panels)
        self.assertIs(package.materials, materials)
        self.assertIs(package.edge_operations, edge_operations)
        self.assertIs(package.machining_operations, machining_operations)
        self.assertIs(package.warnings, warnings)

    def test_build_returns_manufacturing_package(self):
        from manufacturing.manufacturing_package import ManufacturingPackage

        package = self.builder.build()

        self.assertIsInstance(package, ManufacturingPackage)

    def test_build_preserves_empty_inputs_exactly(self):
        panels = []
        materials = []
        edge_operations = []
        machining_operations = []
        warnings = []

        package = self.builder.build(
            panels=panels,
            materials=materials,
            edge_operations=edge_operations,
            machining_operations=machining_operations,
            warnings=warnings,
        )

        self.assertIs(package.panels, panels)
        self.assertIs(package.materials, materials)
        self.assertIs(package.edge_operations, edge_operations)
        self.assertIs(package.machining_operations, machining_operations)
        self.assertIs(package.warnings, warnings)

    def test_builder_exists(self):
        from manufacturing.manufacturing_package_builder import (
            ManufacturingPackageBuilder,
        )

        self.assertTrue(callable(ManufacturingPackageBuilder().build))


if __name__ == "__main__":
    unittest.main()
