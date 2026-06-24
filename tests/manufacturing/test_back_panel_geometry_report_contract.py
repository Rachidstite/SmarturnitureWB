import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestBackPanelGeometryReportContract(unittest.TestCase):

    def test_report_is_dataclass(self):
        from manufacturing.back_panel_geometry_report import (
            BackPanelGeometryReport,
        )

        self.assertTrue(is_dataclass(BackPanelGeometryReport))

    def test_field_order_is_stable(self):
        from manufacturing.back_panel_geometry_report import (
            BackPanelGeometryReport,
        )

        self.assertEqual(
            [field.name for field in fields(BackPanelGeometryReport)],
            ["width", "height"],
        )

    def test_default_width_is_zero(self):
        from manufacturing.back_panel_geometry_report import (
            BackPanelGeometryReport,
        )

        report = BackPanelGeometryReport()

        self.assertEqual(report.width, 0.0)

    def test_default_height_is_zero(self):
        from manufacturing.back_panel_geometry_report import (
            BackPanelGeometryReport,
        )

        report = BackPanelGeometryReport()

        self.assertEqual(report.height, 0.0)

    def test_explicit_dimensions_are_accepted(self):
        from manufacturing.back_panel_geometry_report import (
            BackPanelGeometryReport,
        )

        report = BackPanelGeometryReport(width=1200.5, height=2200.25)

        self.assertEqual(report.width, 1200.5)
        self.assertEqual(report.height, 2200.25)

    def test_passive_container_only(self):
        import manufacturing.back_panel_geometry_report as module

        source = inspect.getsource(module)

        self.assertNotIn("PanelSpec", source)
        self.assertNotIn("runtime", source.lower())
        self.assertNotIn("cnc", source.lower())
        self.assertNotIn("freecad", source.lower())
        self.assertNotIn("build(", source)
        self.assertNotIn("validate(", source)

    def test_no_forbidden_imports(self):
        import manufacturing.back_panel_geometry_report as module

        source = inspect.getsource(module)

        self.assertNotIn("PanelSpec", source)
        self.assertNotIn("domain.manufacturing_ops", source)
        self.assertNotIn("FreeCAD", source)
        self.assertNotIn("CNC", source)
        self.assertNotIn("runtime", source.lower())


if __name__ == "__main__":
    unittest.main()
