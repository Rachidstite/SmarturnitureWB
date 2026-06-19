import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestBackPanelHolePlacementContract(unittest.TestCase):

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

    def test_no_generation_logic(self):
        import manufacturing.back_panel_hole_placement_report as module

        source = inspect.getsource(module)

        self.assertNotIn("for ", source)
        self.assertNotIn("while ", source)
        self.assertNotIn("append(", source)
        self.assertNotIn("ManufacturingCompiler", source)
        self.assertNotIn("FactoryDecisionBuilder", source)
        self.assertNotIn("ProductionReadinessBuilder", source)

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
