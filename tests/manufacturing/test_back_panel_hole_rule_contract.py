import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestBackPanelHoleRuleContract(unittest.TestCase):

    def test_report_contract_exists(self):
        from manufacturing.back_panel_hole_rule_report import (
            BackPanelHoleRuleReport,
        )

        self.assertTrue(is_dataclass(BackPanelHoleRuleReport))

    def test_field_inventory_is_stable(self):
        from manufacturing.back_panel_hole_rule_report import (
            BackPanelHoleRuleReport,
        )

        self.assertEqual(
            [field.name for field in fields(BackPanelHoleRuleReport)],
            [
                "minimum_panel_width",
                "minimum_panel_height",
                "spacing_rule",
                "edge_rule",
                "corner_rule",
                "maximum_spacing",
                "requires_center_holes",
            ],
        )

    def test_safe_defaults(self):
        from manufacturing.back_panel_hole_rule_report import (
            BackPanelHoleRuleReport,
        )

        report = BackPanelHoleRuleReport()

        self.assertEqual(report.minimum_panel_width, 0.0)
        self.assertEqual(report.minimum_panel_height, 0.0)
        self.assertEqual(report.spacing_rule, "")
        self.assertEqual(report.edge_rule, "")
        self.assertEqual(report.corner_rule, "")
        self.assertEqual(report.maximum_spacing, 0.0)
        self.assertFalse(report.requires_center_holes)

    def test_no_generation_logic(self):
        import manufacturing.back_panel_hole_rule_report as module

        source = inspect.getsource(module)

        self.assertNotIn("for ", source)
        self.assertNotIn("while ", source)
        self.assertNotIn("append(", source)
        self.assertNotIn("ManufacturingCompiler", source)
        self.assertNotIn("FactoryDecisionBuilder", source)
        self.assertNotIn("ProductionReadinessBuilder", source)

    def test_no_cnc_or_runtime_imports(self):
        import manufacturing.back_panel_hole_rule_report as module

        source = inspect.getsource(module)

        self.assertNotIn("CNC", source)
        self.assertNotIn("compiler", source.lower())
        self.assertNotIn("runtime", source.lower())

    def test_no_runtime_behavior_changes(self):
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
