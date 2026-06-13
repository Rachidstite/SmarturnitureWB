import unittest


class TestManufacturingCutlistBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.manufacturing_cutlist_builder import (
            ManufacturingCutlistBuilder,
        )

        self.assertTrue(callable(ManufacturingCutlistBuilder().build))

    def test_build_returns_cutlist_report_for_package_panels(self):
        from manufacturing.manufacturing_cutlist_builder import (
            ManufacturingCutlistBuilder,
        )
        from manufacturing.manufacturing_cutlist_report import (
            ManufacturingCutlistReport,
        )
        from manufacturing.manufacturing_package import ManufacturingPackage
        from manufacturing.panel_spec import PanelSpec
        from shared.roles import NodeRole

        panel = PanelSpec(
            identity="side-left",
            role=NodeRole.SIDE_PANEL,
            width=600.0,
            height=720.0,
            thickness=18.0,
            material="MDF_18MM",
            quantity=2,
        )
        package = ManufacturingPackage(
            panels=[panel],
            warnings=["Missing edge data"],
        )

        report = ManufacturingCutlistBuilder().build(package)

        self.assertIsInstance(report, ManufacturingCutlistReport)
        self.assertEqual(
            report.items,
            [
                {
                    "identity": panel.identity,
                    "width": panel.width,
                    "height": panel.height,
                    "thickness": panel.thickness,
                    "material": panel.material,
                    "quantity": panel.quantity,
                }
            ],
        )
        self.assertEqual(report.total_items, 1)
        self.assertIs(report.warnings, package.warnings)


if __name__ == "__main__":
    unittest.main()
