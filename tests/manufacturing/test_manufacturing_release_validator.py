import unittest


class TestManufacturingReleaseValidator(unittest.TestCase):

    def setUp(self):
        from manufacturing.manufacturing_release_validator import (
            ManufacturingReleaseValidator,
        )

        self.validator = ManufacturingReleaseValidator()

    def test_release_validator_exists(self):
        self.assertTrue(callable(self.validator.validate))

    def test_empty_package_is_not_ready(self):
        from manufacturing.manufacturing_package import ManufacturingPackage

        result = self.validator.validate(ManufacturingPackage())

        self.assertEqual(
            result,
            {
                "ready": False,
                "warnings": [
                    "No panels",
                    "No materials",
                    "No machining operations",
                    "No edge operations",
                ],
            },
        )

    def test_invalid_panel_is_not_ready(self):
        package = self._valid_package()
        package.panels[0].width = 0

        result = self.validator.validate(package)

        self.assertFalse(result["ready"])
        self.assertIn("Invalid panel width", result["warnings"])

    def test_valid_package_is_ready(self):
        result = self.validator.validate(self._valid_package())

        self.assertEqual(result, {"ready": True, "warnings": []})

    @staticmethod
    def _valid_package():
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
                UnifiedManufacturingOperation(operation_type="DRILL")
            ],
            edge_operations=[
                UnifiedManufacturingOperation(operation_type="EDGE_BANDING")
            ],
        )


if __name__ == "__main__":
    unittest.main()
