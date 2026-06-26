import importlib
import inspect
import re
import unittest


class TestPanelThicknessReadinessRule(unittest.TestCase):
    def test_passing_panel_with_positive_thickness(self):
        from manufacturing.panel_spec import PanelSpec
        from manufacturing.panel_thickness_readiness_rule import (
            evaluate_panel_thickness_readiness,
        )
        from shared.roles import NodeRole

        result = evaluate_panel_thickness_readiness(
            PanelSpec(
                identity="panel-1",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=18.0,
                material="MDF_18MM",
            )
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_failing_panel_with_zero_thickness(self):
        from manufacturing.panel_spec import PanelSpec
        from manufacturing.panel_thickness_readiness_rule import (
            evaluate_panel_thickness_readiness,
        )
        from shared.roles import NodeRole

        result = evaluate_panel_thickness_readiness(
            PanelSpec(
                identity="panel-2",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=0.0,
                material="MDF_18MM",
            )
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("panel-2", result.message)
        self.assertIn("0.0", result.message)

    def test_failing_panel_with_negative_thickness(self):
        from manufacturing.panel_spec import PanelSpec
        from manufacturing.panel_thickness_readiness_rule import (
            evaluate_panel_thickness_readiness,
        )
        from shared.roles import NodeRole

        result = evaluate_panel_thickness_readiness(
            PanelSpec(
                identity="panel-3",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=-12.0,
                material="MDF_18MM",
            )
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("panel-3", result.message)
        self.assertIn("-12.0", result.message)

    def test_failure_message_includes_panel_id(self):
        from manufacturing.panel_spec import PanelSpec
        from manufacturing.panel_thickness_readiness_rule import (
            evaluate_panel_thickness_readiness,
        )
        from shared.roles import NodeRole

        result = evaluate_panel_thickness_readiness(
            PanelSpec(
                identity="panel-4",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=0.0,
                material="MDF_18MM",
            )
        )

        self.assertIn("panel-4", result.message)

    def test_failure_message_includes_thickness_value(self):
        from manufacturing.panel_spec import PanelSpec
        from manufacturing.panel_thickness_readiness_rule import (
            evaluate_panel_thickness_readiness,
        )
        from shared.roles import NodeRole

        result = evaluate_panel_thickness_readiness(
            PanelSpec(
                identity="panel-5",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=0.0,
                material="MDF_18MM",
            )
        )

        self.assertIn("0.0", result.message)

    def test_uses_capability_manufacturing_panel_thickness_readiness(self):
        from manufacturing.panel_spec import PanelSpec
        from manufacturing.panel_thickness_readiness_rule import (
            evaluate_panel_thickness_readiness,
        )
        from shared.roles import NodeRole

        result = evaluate_panel_thickness_readiness(
            PanelSpec(
                identity="panel-6",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=1.0,
                material="MDF_18MM",
            )
        )

        self.assertEqual(result.capability, "manufacturing_panel_thickness_readiness")

    def test_uses_component_id_from_panel_identity(self):
        from manufacturing.panel_spec import PanelSpec
        from manufacturing.panel_thickness_readiness_rule import (
            evaluate_panel_thickness_readiness,
        )
        from shared.roles import NodeRole

        result = evaluate_panel_thickness_readiness(
            PanelSpec(
                identity="panel-7",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=18.0,
                material="MDF_18MM",
            )
        )

        self.assertEqual(result.component_id, "panel-7")

    def test_sets_source_correctly(self):
        from manufacturing.panel_spec import PanelSpec
        from manufacturing.panel_thickness_readiness_rule import (
            evaluate_panel_thickness_readiness,
        )
        from shared.roles import NodeRole

        result = evaluate_panel_thickness_readiness(
            PanelSpec(
                identity="panel-8",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=18.0,
                material="MDF_18MM",
            )
        )

        self.assertEqual(result.source, "panel-thickness-readiness-rule")

    def test_import_without_freecad(self):
        module = importlib.import_module("manufacturing.panel_thickness_readiness_rule")
        source = inspect.getsource(module)

        self.assertIn("evaluate_panel_thickness_readiness", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_duplicate_panel_class(self):
        module = importlib.import_module("manufacturing.panel_thickness_readiness_rule")
        source = inspect.getsource(module)

        self.assertNotIn("class Panel", source)
        self.assertNotIn("class Panel(", source)
        self.assertNotIn("Panel =", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("manufacturing.panel_thickness_readiness_rule")
        source = inspect.getsource(module)

        for token in (
            "SceneGraph",
            "UI",
            "CNC",
            "export",
            "cost",
            "nesting",
            "geometry",
            "FreeCAD",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))
        self.assertIsNone(re.search(r"\bEngine\b", source))

    def test_function_signature_remains_generic(self):
        from manufacturing.panel_thickness_readiness_rule import (
            evaluate_panel_thickness_readiness,
        )

        signature = inspect.signature(evaluate_panel_thickness_readiness)
        self.assertEqual(
            list(signature.parameters),
            ["panel", "rule_id", "source"],
        )
        self.assertNotIn("self", signature.parameters)
        self.assertNotIn("cls", signature.parameters)

    def test_does_not_contain_engine_terminology(self):
        module = importlib.import_module("manufacturing.panel_thickness_readiness_rule")
        source = inspect.getsource(module)

        self.assertNotIn("Engine", source)
        self.assertIsNone(re.search(r"\bEngine\b", source))


if __name__ == "__main__":
    unittest.main()
