import unittest


class TestManufacturingEdgeBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.manufacturing_edge_builder import (
            ManufacturingEdgeBuilder,
        )

        self.assertTrue(callable(ManufacturingEdgeBuilder().build))

    def test_build_returns_edge_report_for_panel_edges(self):
        from manufacturing.edge_spec import EdgeSpec
        from manufacturing.manufacturing_edge_builder import (
            ManufacturingEdgeBuilder,
        )
        from manufacturing.manufacturing_edge_report import (
            ManufacturingEdgeReport,
        )
        from manufacturing.manufacturing_package import ManufacturingPackage
        from manufacturing.panel_spec import PanelSpec
        from shared.roles import NodeRole

        panel = PanelSpec(
            identity="door-01",
            role=NodeRole.DOOR_PANEL,
            width=600,
            height=720,
            thickness=18,
            material="MDF_18MM",
            edge_spec=EdgeSpec(
                top="ABS_1MM",
                bottom=None,
                left=None,
                right="ABS_1MM",
            ),
        )
        package = ManufacturingPackage(
            panels=[panel],
            warnings=["Missing edge data"],
        )

        report = ManufacturingEdgeBuilder().build(package)

        self.assertIsInstance(report, ManufacturingEdgeReport)
        self.assertEqual(
            report.items,
            [
                {
                    "panel_identity": "door-01",
                    "edge": "TOP",
                    "banding": "ABS_1MM",
                    "linear_meters": 0.6,
                },
                {
                    "panel_identity": "door-01",
                    "edge": "RIGHT",
                    "banding": "ABS_1MM",
                    "linear_meters": 0.72,
                },
            ],
        )
        self.assertEqual(report.total_items, 2)
        self.assertEqual(report.total_linear_meters, 1.32)
        self.assertIs(report.warnings, package.warnings)


if __name__ == "__main__":
    unittest.main()
