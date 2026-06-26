import importlib
import inspect
import re
import unittest


class TestPanelEdgeReadinessRule(unittest.TestCase):
    def test_passing_panel_with_edge_data(self):
        from manufacturing.edge_spec import EdgeSpec
        from manufacturing.panel_edge_readiness_rule import (
            evaluate_panel_edge_readiness,
        )
        from manufacturing.panel_spec import PanelSpec
        from shared.roles import NodeRole

        result = evaluate_panel_edge_readiness(
            PanelSpec(
                identity="panel-1",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=18.0,
                material="MDF_18MM",
                edge_spec=EdgeSpec(right="ABS_1MM"),
            )
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_failing_panel_without_edge_data(self):
        from manufacturing.panel_edge_readiness_rule import (
            evaluate_panel_edge_readiness,
        )
        from manufacturing.panel_spec import PanelSpec
        from shared.roles import NodeRole

        result = evaluate_panel_edge_readiness(
            PanelSpec(
                identity="panel-2",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=18.0,
                material="MDF_18MM",
            )
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("panel-2", result.message)
        self.assertEqual(result.capability, "manufacturing_panel_edge_readiness")
        self.assertEqual(result.component_id, "panel-2")

    def test_message_includes_panel_identity(self):
        from manufacturing.panel_edge_readiness_rule import (
            evaluate_panel_edge_readiness,
        )
        from manufacturing.panel_spec import PanelSpec
        from shared.roles import NodeRole

        result = evaluate_panel_edge_readiness(
            PanelSpec(
                identity="panel-3",
                role=NodeRole.SIDE_PANEL,
                width=600.0,
                height=720.0,
                thickness=18.0,
                material="MDF_18MM",
            )
        )

        self.assertIn("panel-3", result.message)

    def test_no_freecad_import(self):
        module = importlib.import_module("manufacturing.panel_edge_readiness_rule")
        source = inspect.getsource(module)

        self.assertIn("evaluate_panel_edge_readiness", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_duplicate_panel_class(self):
        module = importlib.import_module("manufacturing.panel_edge_readiness_rule")
        source = inspect.getsource(module)

        self.assertNotIn("class Panel", source)
        self.assertNotIn("class Panel(", source)
        self.assertNotIn("Panel =", source)

    def test_no_duplicate_edge_class(self):
        module = importlib.import_module("manufacturing.panel_edge_readiness_rule")
        source = inspect.getsource(module)

        self.assertNotIn("class Edge", source)
        self.assertNotIn("class Edge(", source)
        self.assertNotIn("Edge =", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("manufacturing.panel_edge_readiness_rule")
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
        from manufacturing.panel_edge_readiness_rule import (
            evaluate_panel_edge_readiness,
        )

        signature = inspect.signature(evaluate_panel_edge_readiness)
        self.assertEqual(
            list(signature.parameters),
            ["panel", "rule_id", "source"],
        )
        self.assertNotIn("self", signature.parameters)
        self.assertNotIn("cls", signature.parameters)

    def test_does_not_contain_engine_terminology(self):
        module = importlib.import_module("manufacturing.panel_edge_readiness_rule")
        source = inspect.getsource(module)

        self.assertNotIn("Engine", source)
        self.assertIsNone(re.search(r"\bEngine\b", source))


if __name__ == "__main__":
    unittest.main()
