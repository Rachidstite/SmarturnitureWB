import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestBackPanelHolePlacementContract(unittest.TestCase):

    def test_coordinate_contract_exists(self):
        from manufacturing.back_panel_hole_placement_report import (
            BackPanelHoleCoordinate,
        )

        self.assertTrue(is_dataclass(BackPanelHoleCoordinate))

    def test_coordinate_field_inventory_is_stable(self):
        from manufacturing.back_panel_hole_placement_report import (
            BackPanelHoleCoordinate,
        )

        self.assertEqual(
            [field.name for field in fields(BackPanelHoleCoordinate)],
            ["x", "y", "diameter", "depth", "face"],
        )

    def test_coordinate_safe_defaults(self):
        from manufacturing.back_panel_hole_placement_report import (
            BackPanelHoleCoordinate,
        )

        coordinate = BackPanelHoleCoordinate()

        self.assertEqual(coordinate.x, 0.0)
        self.assertEqual(coordinate.y, 0.0)
        self.assertEqual(coordinate.diameter, 0.0)
        self.assertEqual(coordinate.depth, 0.0)
        self.assertEqual(coordinate.face, "")

    def test_report_contract_exists(self):
        from manufacturing.back_panel_hole_placement_report import (
            BackPanelHolePlacementReport,
        )

        self.assertTrue(is_dataclass(BackPanelHolePlacementReport))

    def test_field_inventory_is_stable(self):
        from manufacturing.back_panel_hole_placement_report import (
            BackPanelHolePlacementReport,
        )

        self.assertEqual(
            [field.name for field in fields(BackPanelHolePlacementReport)],
            [
                "edge_distance",
                "corner_offset",
                "minimum_hole_count",
                "maximum_hole_count",
                "default_spacing",
                "supports_screws",
                "supports_confirmat",
                "hole_positions",
            ],
        )

    def test_safe_defaults(self):
        from manufacturing.back_panel_hole_placement_report import (
            BackPanelHolePlacementReport,
        )

        report = BackPanelHolePlacementReport()

        self.assertEqual(report.edge_distance, 0.0)
        self.assertEqual(report.corner_offset, 0.0)
        self.assertEqual(report.minimum_hole_count, 0)
        self.assertEqual(report.maximum_hole_count, 0)
        self.assertEqual(report.default_spacing, 0.0)
        self.assertFalse(report.supports_screws)
        self.assertFalse(report.supports_confirmat)
        self.assertEqual(report.hole_positions, [])

    def test_instances_do_not_share_hole_positions(self):
        from manufacturing.back_panel_hole_placement_report import (
            BackPanelHolePlacementReport,
        )

        first = BackPanelHolePlacementReport()
        second = BackPanelHolePlacementReport()

        first.hole_positions.append(object())

        self.assertEqual(len(second.hole_positions), 0)
        self.assertIsNot(first.hole_positions, second.hole_positions)

    def test_report_accepts_coordinate_objects(self):
        from manufacturing.back_panel_hole_placement_report import (
            BackPanelHoleCoordinate,
            BackPanelHolePlacementReport,
        )

        coordinates = [BackPanelHoleCoordinate(x=12.5, y=8.0, face="back")]
        report = BackPanelHolePlacementReport(hole_positions=coordinates)

        self.assertIs(report.hole_positions, coordinates)
        self.assertIs(report.hole_positions[0], coordinates[0])

    def test_existing_fields_remain_backward_compatible(self):
        from manufacturing.back_panel_hole_placement_report import (
            BackPanelHolePlacementReport,
        )

        report = BackPanelHolePlacementReport(
            edge_distance=1.5,
            corner_offset=2.5,
            minimum_hole_count=3,
            maximum_hole_count=4,
            default_spacing=5.5,
            supports_screws=True,
            supports_confirmat=True,
        )

        self.assertEqual(report.edge_distance, 1.5)
        self.assertEqual(report.corner_offset, 2.5)
        self.assertEqual(report.minimum_hole_count, 3)
        self.assertEqual(report.maximum_hole_count, 4)
        self.assertEqual(report.default_spacing, 5.5)
        self.assertTrue(report.supports_screws)
        self.assertTrue(report.supports_confirmat)
        self.assertEqual(report.hole_positions, [])

    def test_no_generation_logic(self):
        import manufacturing.back_panel_hole_placement_report as module

        source = inspect.getsource(module)

        self.assertNotIn("for ", source)
        self.assertNotIn("while ", source)
        self.assertNotIn("append(", source)
        self.assertNotIn("ManufacturingCompiler", source)
        self.assertNotIn("FactoryDecisionBuilder", source)
        self.assertNotIn("ProductionReadinessBuilder", source)
        self.assertNotIn("HoleSpec", source)
        self.assertNotIn("HardwareSpec", source)
        self.assertNotIn("hardware_library", source)

    def test_no_runtime_changes(self):
        from domain.back_panel_engine import BackPanelEngine, BackPanelRule

        rule = BackPanelRule()

        self.assertEqual(
            BackPanelEngine.groove_width(rule),
            rule.thickness + rule.groove_clearance,
        )
        self.assertEqual(BackPanelEngine.insertion_depth(rule), rule.groove_depth)
        self.assertEqual(BackPanelEngine.offset(rule), rule.groove_offset)


if __name__ == "__main__":
    unittest.main()
