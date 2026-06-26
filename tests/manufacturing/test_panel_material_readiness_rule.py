import importlib
import inspect
import re
import unittest


class TestPanelMaterialReadinessRule(unittest.TestCase):
    def test_passing_panel_with_material(self):
        from manufacturing.panel_material_readiness_rule import (
            evaluate_panel_material_readiness,
        )
        from manufacturing.panel_spec import PanelSpec
        from shared.roles import NodeRole

        result = evaluate_panel_material_readiness(
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
        self.assertEqual(result.capability, "manufacturing_material_readiness")
        self.assertEqual(result.component_id, "panel-1")

    def test_failing_panel_without_material(self):
        from manufacturing.panel_material_readiness_rule import (
            evaluate_panel_material_readiness,
        )
        from manufacturing.panel_spec import PanelSpec
        from shared.roles import NodeRole

        result = evaluate_panel_material_readiness(
            PanelSpec(
                identity="panel-2",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=18.0,
                material="",
            )
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("panel-2", result.message)
        self.assertEqual(result.capability, "manufacturing_material_readiness")
        self.assertEqual(result.component_id, "panel-2")

    def test_message_includes_panel_id(self):
        from manufacturing.panel_material_readiness_rule import (
            evaluate_panel_material_readiness,
        )
        from manufacturing.panel_spec import PanelSpec
        from shared.roles import NodeRole

        result = evaluate_panel_material_readiness(
            PanelSpec(
                identity="panel-3",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=18.0,
                material="",
            )
        )

        self.assertIn("panel-3", result.message)

    def test_no_freecad_import(self):
        module = importlib.import_module("manufacturing.panel_material_readiness_rule")
        source = inspect.getsource(module)

        self.assertIn("evaluate_panel_material_readiness", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_duplicate_panel_class(self):
        module = importlib.import_module("manufacturing.panel_material_readiness_rule")
        source = inspect.getsource(module)

        self.assertNotIn("class Panel", source)
        self.assertNotIn("class Panel(", source)
        self.assertNotIn("Panel =", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("manufacturing.panel_material_readiness_rule")
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
        from manufacturing.panel_material_readiness_rule import (
            evaluate_panel_material_readiness,
        )

        signature = inspect.signature(evaluate_panel_material_readiness)
        self.assertEqual(
            list(signature.parameters),
            ["panel", "rule_id", "source"],
        )
        self.assertNotIn("self", signature.parameters)
        self.assertNotIn("cls", signature.parameters)

    def test_does_not_contain_engine_terminology(self):
        module = importlib.import_module("manufacturing.panel_material_readiness_rule")
        source = inspect.getsource(module)

        self.assertNotIn("Engine", source)
        self.assertIsNone(re.search(r"\bEngine\b", source))


if __name__ == "__main__":
    unittest.main()
