import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestBackPanelHolePatternContract(unittest.TestCase):

    def test_report_contract_exists(self):
        from manufacturing.back_panel_hole_pattern_report import (
            BackPanelHolePatternReport,
        )

        self.assertTrue(is_dataclass(BackPanelHolePatternReport))

    def test_field_inventory_is_stable(self):
        from manufacturing.back_panel_hole_pattern_report import (
            BackPanelHolePatternReport,
        )

        self.assertEqual(
            [field.name for field in fields(BackPanelHolePatternReport)],
            [
                "horizontal_hole_count",
                "vertical_hole_count",
                "total_hole_count",
                "top_edge_holes",
                "bottom_edge_holes",
                "left_edge_holes",
                "right_edge_holes",
                "pattern_type",
                "center_hole_count",
            ],
        )

    def test_safe_defaults(self):
        from manufacturing.back_panel_hole_pattern_report import (
            BackPanelHolePatternReport,
        )

        report = BackPanelHolePatternReport()

        self.assertEqual(report.horizontal_hole_count, 0)
        self.assertEqual(report.vertical_hole_count, 0)
        self.assertEqual(report.total_hole_count, 0)
        self.assertEqual(report.top_edge_holes, 0)
        self.assertEqual(report.bottom_edge_holes, 0)
        self.assertEqual(report.left_edge_holes, 0)
        self.assertEqual(report.right_edge_holes, 0)
        self.assertEqual(report.pattern_type, "")
        self.assertEqual(report.center_hole_count, 0)

    def test_no_generation_logic(self):
        import manufacturing.back_panel_hole_pattern_report as module

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
