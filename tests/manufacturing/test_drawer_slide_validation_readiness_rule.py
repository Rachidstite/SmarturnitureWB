import inspect
import unittest
from types import SimpleNamespace


class TestDrawerSlideValidationReadinessRule(unittest.TestCase):

    def setUp(self):
        from manufacturing.drawer_slide_validation_readiness_rule import (
            evaluate_drawer_slide_validation_readiness,
        )

        self.evaluate = evaluate_drawer_slide_validation_readiness

    def test_passing_report_with_valid_values(self):
        from manufacturing.drawer_validation_report import DrawerValidationReport

        report = DrawerValidationReport(
            is_valid=True,
            manufacturing_ready=True,
            slide_installation_valid=True,
            clearance_valid=True,
            hardware_complete=True,
        )
        report.drawer_width = 500.0
        report.drawer_depth = 400.0
        report.slide_length = 350.0

        result = self.evaluate(report)

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_zero_width_fails(self):
        result = self.evaluate(self._report(drawer_width=0))

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("drawer_width", result.message)

    def test_zero_depth_fails(self):
        result = self.evaluate(self._report(drawer_depth=0))

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("drawer_depth", result.message)

    def test_zero_slide_length_fails(self):
        result = self.evaluate(self._report(slide_length=0))

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("slide_length", result.message)

    def test_incomplete_hardware_fails(self):
        result = self.evaluate(self._report(hardware_complete=False))

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("hardware_complete", result.message)

    def test_message_includes_all_fields_on_failure(self):
        result = self.evaluate(
            self._report(
                drawer_width=0,
                drawer_depth=0,
                slide_length=0,
                hardware_complete=False,
            )
        )

        self.assertIn("drawer_width", result.message)
        self.assertIn("drawer_depth", result.message)
        self.assertIn("slide_length", result.message)
        self.assertIn("hardware_complete", result.message)

    def test_capability_is_correct(self):
        result = self.evaluate(self._report())

        self.assertEqual(result.capability, "manufacturing_drawer_slide_validation_readiness")

    def test_component_id_is_correct(self):
        result = self.evaluate(self._report())

        self.assertEqual(result.component_id, "drawer-slide-validation")

    def test_source_is_correct(self):
        result = self.evaluate(self._report())

        self.assertEqual(result.source, "drawer-slide-validation-readiness-rule")

    def test_imports_without_freecad(self):
        import manufacturing.drawer_slide_validation_readiness_rule as module

        self.assertNotIn("FreeCAD", inspect.getsource(module))

    def test_no_duplicate_drawer_or_drawer_slide_dto(self):
        import manufacturing.drawer_slide_validation_readiness_rule as module

        source = inspect.getsource(module)
        self.assertNotIn("class Drawer", source)
        self.assertNotIn("class DrawerSlide", source)

    def test_no_banned_imports(self):
        import manufacturing.drawer_slide_validation_readiness_rule as module

        source = inspect.getsource(module)
        for banned in [
            "FreeCAD",
            "SceneGraph",
            "UI",
            "CNC",
            "export",
            "cost",
            "nesting",
            "geometry",
            "DrawerSlideRule",
        ]:
            self.assertNotIn(banned, source)

    def test_function_signature_remains_generic(self):
        from manufacturing.drawer_slide_validation_readiness_rule import (
            evaluate_drawer_slide_validation_readiness,
        )

        signature = inspect.signature(evaluate_drawer_slide_validation_readiness)

        self.assertEqual(list(signature.parameters), ["report"])

    def test_existing_drawer_validation_builder_tests_still_pass(self):
        from manufacturing.drawer_validation_builder import DrawerValidationBuilder

        builder = DrawerValidationBuilder()
        report = builder.build(self._rules_report())

        self.assertTrue(report.is_valid)
        self.assertTrue(report.manufacturing_ready)

    def test_manufacturing_validation_builder_tests_still_pass(self):
        from manufacturing.drawer_slide_validation_readiness_rule import (
            evaluate_drawer_slide_validation_readiness,
        )
        from manufacturing.manufacturing_validation_builder import (
            build_manufacturing_validation_report,
        )

        rule_result = evaluate_drawer_slide_validation_readiness(self._report())
        report = build_manufacturing_validation_report([rule_result])

        self.assertTrue(report.ready_for_manufacturing)
        self.assertEqual(report.total_rule_count, 1)

    @staticmethod
    def _report(
        drawer_width=500.0,
        drawer_depth=400.0,
        slide_length=350.0,
        hardware_complete=True,
    ):
        from manufacturing.drawer_validation_report import DrawerValidationReport

        report = DrawerValidationReport(
            is_valid=True,
            manufacturing_ready=True,
            slide_installation_valid=True,
            clearance_valid=True,
            hardware_complete=hardware_complete,
        )
        report.drawer_width = drawer_width
        report.drawer_depth = drawer_depth
        report.slide_length = slide_length
        return report

    @staticmethod
    def _rules_report(
        drawer_width=500.0,
        drawer_depth=400.0,
        slide_length=350.0,
        bottom_panel_thickness=8.0,
        hardware_complete=True,
        tags=None,
    ):
        return SimpleNamespace(
            drawer_width=drawer_width,
            drawer_depth=drawer_depth,
            slide_length=slide_length,
            bottom_panel_thickness=bottom_panel_thickness,
            hardware_complete=hardware_complete,
            tags=list(tags or []),
        )


if __name__ == "__main__":
    unittest.main()
