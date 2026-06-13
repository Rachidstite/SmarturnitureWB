import unittest


class TestManufacturingValidator(unittest.TestCase):

    def setUp(self):
        from manufacturing.manufacturing_validator import ManufacturingValidator

        self.validator = ManufacturingValidator()

    def test_validator_exists(self):
        self.assertTrue(callable(self.validator.validate))

    def test_invalid_panel_dimensions_return_warnings(self):
        package = self._valid_package()
        package.panels[0].width = 0
        package.panels[0].height = -1
        package.panels[0].thickness = 0

        self.assertEqual(
            self.validator.validate(package),
            [
                "Invalid panel width",
                "Invalid panel height",
                "Invalid panel thickness",
            ],
        )

    def test_missing_material_name_returns_warning(self):
        package = self._valid_package()
        package.materials[0].name = ""

        self.assertEqual(
            self.validator.validate(package),
            ["Missing material name"],
        )

    def test_missing_machining_operation_type_returns_warning(self):
        package = self._valid_package(machining_operation_type="")

        self.assertEqual(
            self.validator.validate(package),
            ["Missing operation type"],
        )

    def test_missing_edge_operation_type_returns_warning(self):
        package = self._valid_package(edge_operation_type="")

        self.assertEqual(
            self.validator.validate(package),
            ["Missing operation type"],
        )

    def test_valid_package_returns_no_warnings(self):
        self.assertEqual(self.validator.validate(self._valid_package()), [])

    @staticmethod
    def _valid_package(
        machining_operation_type="DRILL",
        edge_operation_type="EDGE_BANDING",
    ):
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
                    identity="side-left",
                    role=NodeRole.SIDE_PANEL,
                    width=600.0,
                    height=720.0,
                    thickness=18.0,
                    material="MDF_18MM",
                )
            ],
            materials=[MaterialSpec(name="MDF_18MM", thickness=18.0)],
            machining_operations=[
                UnifiedManufacturingOperation(
                    operation_type=machining_operation_type
                )
            ],
            edge_operations=[
                UnifiedManufacturingOperation(operation_type=edge_operation_type)
            ],
        )


if __name__ == "__main__":
    unittest.main()
