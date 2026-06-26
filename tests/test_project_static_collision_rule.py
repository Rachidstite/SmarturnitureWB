import importlib
import inspect
import re
import unittest

from project_engineering.project_collision_fact import ProjectCollisionFact


class TestProjectStaticCollisionRule(unittest.TestCase):
    def test_error_collision_fails_with_severity_error(self):
        from project_engineering.project_static_collision_rule import (
            evaluate_project_static_collision,
        )

        result = evaluate_project_static_collision(
            ProjectCollisionFact(
                first_component_id="COMP-A",
                second_component_id="COMP-B",
                severity="error",
            )
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")

    def test_warning_collision_fails_with_severity_warning(self):
        from project_engineering.project_static_collision_rule import (
            evaluate_project_static_collision,
        )

        result = evaluate_project_static_collision(
            ProjectCollisionFact(
                first_component_id="COMP-C",
                second_component_id="COMP-D",
                severity="warning",
            )
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "warning")

    def test_message_includes_first_component_id(self):
        from project_engineering.project_static_collision_rule import (
            evaluate_project_static_collision,
        )

        result = evaluate_project_static_collision(
            ProjectCollisionFact(
                first_component_id="COMP-E",
                second_component_id="COMP-F",
                severity="error",
            )
        )

        self.assertIn("COMP-E", result.message)

    def test_message_includes_second_component_id(self):
        from project_engineering.project_static_collision_rule import (
            evaluate_project_static_collision,
        )

        result = evaluate_project_static_collision(
            ProjectCollisionFact(
                first_component_id="COMP-G",
                second_component_id="COMP-H",
                severity="warning",
            )
        )

        self.assertIn("COMP-H", result.message)

    def test_uses_capability_project_static_collision(self):
        from project_engineering.project_static_collision_rule import (
            evaluate_project_static_collision,
        )

        result = evaluate_project_static_collision(
            ProjectCollisionFact(
                first_component_id="COMP-I",
                second_component_id="COMP-J",
                severity="error",
            )
        )

        self.assertEqual(result.capability, "project_static_collision")

    def test_uses_component_id_from_first_component_id(self):
        from project_engineering.project_static_collision_rule import (
            evaluate_project_static_collision,
        )

        result = evaluate_project_static_collision(
            ProjectCollisionFact(
                first_component_id="COMP-K",
                second_component_id="COMP-L",
                severity="error",
            )
        )

        self.assertEqual(result.component_id, "COMP-K")

    def test_sets_source_correctly(self):
        from project_engineering.project_static_collision_rule import (
            evaluate_project_static_collision,
        )

        result = evaluate_project_static_collision(
            ProjectCollisionFact(
                first_component_id="COMP-M",
                second_component_id="COMP-N",
                severity="warning",
            )
        )

        self.assertEqual(result.source, "project-static-collision-rule")

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.project_static_collision_rule"
        )
        source = inspect.getsource(module)

        self.assertIn("evaluate_project_static_collision", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.project_static_collision_rule"
        )
        source = inspect.getsource(module)

        for token in (
            "collision calculation",
            "geometry",
            "motion",
            "builder",
            "aggregator",
            "decision",
            "Engine",
            "FurnitureProject",
            "CabinetPlacement",
            "SceneGraph",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "FreeCAD",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_function_signature_remains_generic(self):
        from project_engineering.project_static_collision_rule import (
            evaluate_project_static_collision,
        )

        signature = inspect.signature(evaluate_project_static_collision)
        self.assertEqual(list(signature.parameters), ["collision", "rule_id", "source"])
        self.assertNotIn("self", signature.parameters)
        self.assertNotIn("cls", signature.parameters)

    def test_does_not_contain_engine_terminology(self):
        module = importlib.import_module(
            "project_engineering.project_static_collision_rule"
        )
        source = inspect.getsource(module)

        self.assertNotIn("Engine", source)
        self.assertIsNone(re.search(r"\bEngine\b", source))


if __name__ == "__main__":
    unittest.main()
