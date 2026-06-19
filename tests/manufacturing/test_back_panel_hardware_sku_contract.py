import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestBackPanelHardwareSkuContract(unittest.TestCase):

    def test_sku_enum_exists(self):
        from manufacturing.back_panel_hardware_sku import (
            BackPanelHardwareSku,
        )

        self.assertTrue(hasattr(BackPanelHardwareSku, "BACK_PANEL_SCREW"))
        self.assertTrue(hasattr(BackPanelHardwareSku, "BACK_PANEL_CONFIRMAT"))
        self.assertTrue(hasattr(BackPanelHardwareSku, "BACK_PANEL_STAPLE"))

    def test_three_skus_exist(self):
        from manufacturing.back_panel_hardware_sku import (
            BackPanelHardwareSku,
        )

        self.assertEqual(
            [sku.value for sku in BackPanelHardwareSku],
            [
                "BACK_PANEL_SCREW",
                "BACK_PANEL_CONFIRMAT",
                "BACK_PANEL_STAPLE",
            ],
        )

    def test_report_contract_exists(self):
        from manufacturing.back_panel_hardware_report import (
            BackPanelHardwareReport,
        )

        self.assertTrue(is_dataclass(BackPanelHardwareReport))

    def test_field_inventory_is_stable(self):
        from manufacturing.back_panel_hardware_report import (
            BackPanelHardwareReport,
        )

        self.assertEqual(
            [field.name for field in fields(BackPanelHardwareReport)],
            [
                "sku",
                "requires_holes",
                "requires_fasteners",
                "default_hole_diameter",
                "default_hole_depth",
                "default_spacing",
                "manufacturing_notes",
            ],
        )

    def test_screw_contract_valid(self):
        from manufacturing.back_panel_hardware_report import (
            BackPanelHardwareReport,
        )
        from manufacturing.back_panel_hardware_sku import (
            BackPanelHardwareSku,
        )

        report = BackPanelHardwareReport(
            sku=BackPanelHardwareSku.BACK_PANEL_SCREW,
            requires_holes=True,
            requires_fasteners=True,
        )

        self.assertTrue(report.requires_holes)
        self.assertTrue(report.requires_fasteners)

    def test_confirmat_contract_valid(self):
        from manufacturing.back_panel_hardware_report import (
            BackPanelHardwareReport,
        )
        from manufacturing.back_panel_hardware_sku import (
            BackPanelHardwareSku,
        )

        report = BackPanelHardwareReport(
            sku=BackPanelHardwareSku.BACK_PANEL_CONFIRMAT,
            requires_holes=True,
            requires_fasteners=True,
        )

        self.assertTrue(report.requires_holes)
        self.assertTrue(report.requires_fasteners)

    def test_staple_contract_valid(self):
        from manufacturing.back_panel_hardware_report import (
            BackPanelHardwareReport,
        )
        from manufacturing.back_panel_hardware_sku import (
            BackPanelHardwareSku,
        )

        report = BackPanelHardwareReport(
            sku=BackPanelHardwareSku.BACK_PANEL_STAPLE,
            requires_holes=False,
            requires_fasteners=True,
        )

        self.assertFalse(report.requires_holes)
        self.assertTrue(report.requires_fasteners)

    def test_no_runtime_imports(self):
        import manufacturing.back_panel_hardware_report as report_module
        import manufacturing.back_panel_hardware_sku as sku_module

        report_source = inspect.getsource(report_module)
        sku_source = inspect.getsource(sku_module)

        self.assertNotIn("FactoryDecisionBuilder", report_source)
        self.assertNotIn("FactoryDecisionBuilder", sku_source)
        self.assertNotIn("ProductionReadinessBuilder", report_source)
        self.assertNotIn("ProductionReadinessBuilder", sku_source)
        self.assertNotIn("FactoryDecisionIntelligenceBuilder", report_source)
        self.assertNotIn("FactoryDecisionIntelligenceBuilder", sku_source)

    def test_no_manufacturing_behavior_changes(self):
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
