import importlib
import inspect
import re
import unittest


class TestDoorHingeEngineeringReadinessRule(unittest.TestCase):
    def test_passing_report_with_hinge_requirement_and_positive_recommended_count(self):
        from manufacturing.door_engineering_report import DoorEngineeringReport
        from manufacturing.door_hinge_engineering_readiness_rule import (
            evaluate_door_hinge_engineering_readiness,
        )

        result = evaluate_door_hinge_engineering_readiness(
            DoorEngineeringReport(
                hinge_requirement="MEDIUM",
                recommended_hinge_count=3,
            )
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_failing_report_with_empty_hinge_requirement(self):
        from manufacturing.door_engineering_report import DoorEngineeringReport
        from manufacturing.door_hinge_engineering_readiness_rule import (
            evaluate_door_hinge_engineering_readiness,
        )

        result = evaluate_door_hinge_engineering_readiness(
            DoorEngineeringReport(
                hinge_requirement="",
                recommended_hinge_count=3,
            )
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("hinge_requirement=", result.message)
        self.assertIn("recommended_hinge_count=3", result.message)

    def test_failing_report_with_zero_recommended_hinge_count(self):
        from manufacturing.door_engineering_report import DoorEngineeringReport
        from manufacturing.door_hinge_engineering_readiness_rule import (
            evaluate_door_hinge_engineering_readiness,
        )

        result = evaluate_door_hinge_engineering_readiness(
            DoorEngineeringReport(
                hinge_requirement="LOW",
                recommended_hinge_count=0,
            )
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("hinge_requirement=LOW", result.message)
        self.assertIn("recommended_hinge_count=0", result.message)

    def test_failing_report_with_negative_recommended_hinge_count(self):
        from manufacturing.door_engineering_report import DoorEngineeringReport
        from manufacturing.door_hinge_engineering_readiness_rule import (
            evaluate_door_hinge_engineering_readiness,
        )

        result = evaluate_door_hinge_engineering_readiness(
            DoorEngineeringReport(
                hinge_requirement="HIGH",
                recommended_hinge_count=-1,
            )
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("hinge_requirement=HIGH", result.message)
        self.assertIn("recommended_hinge_count=-1", result.message)

    def test_uses_capability_manufacturing_door_hinge_engineering_readiness(self):
        from manufacturing.door_engineering_report import DoorEngineeringReport
        from manufacturing.door_hinge_engineering_readiness_rule import (
            evaluate_door_hinge_engineering_readiness,
        )

        result = evaluate_door_hinge_engineering_readiness(
            DoorEngineeringReport(
                hinge_requirement="LOW",
                recommended_hinge_count=2,
            )
        )

        self.assertEqual(
            result.capability,
            "manufacturing_door_hinge_engineering_readiness",
        )

    def test_uses_component_id_door_hinge_engineering(self):
        from manufacturing.door_engineering_report import DoorEngineeringReport
        from manufacturing.door_hinge_engineering_readiness_rule import (
            evaluate_door_hinge_engineering_readiness,
        )

        result = evaluate_door_hinge_engineering_readiness(
            DoorEngineeringReport(
                hinge_requirement="LOW",
                recommended_hinge_count=2,
            )
        )

        self.assertEqual(result.component_id, "door-hinge-engineering")

    def test_sets_source_correctly(self):
        from manufacturing.door_engineering_report import DoorEngineeringReport
        from manufacturing.door_hinge_engineering_readiness_rule import (
            evaluate_door_hinge_engineering_readiness,
        )

        result = evaluate_door_hinge_engineering_readiness(
            DoorEngineeringReport(
                hinge_requirement="LOW",
                recommended_hinge_count=2,
            )
        )

        self.assertEqual(
            result.source,
            "door-hinge-engineering-readiness-rule",
        )

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "manufacturing.door_hinge_engineering_readiness_rule"
        )
        source = inspect.getsource(module)

        self.assertIn("evaluate_door_hinge_engineering_readiness", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_duplicate_hinge_or_door_engineering_dto(self):
        module = importlib.import_module(
            "manufacturing.door_hinge_engineering_readiness_rule"
        )
        source = inspect.getsource(module)

        self.assertNotIn("class Hinge", source)
        self.assertNotIn("class DoorEngineering", source)
        self.assertNotIn("DoorEngineeringReport(", source)
        self.assertNotIn("HingeRule", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "manufacturing.door_hinge_engineering_readiness_rule"
        )
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
        from manufacturing.door_hinge_engineering_readiness_rule import (
            evaluate_door_hinge_engineering_readiness,
        )

        signature = inspect.signature(evaluate_door_hinge_engineering_readiness)
        self.assertEqual(list(signature.parameters), ["report", "rule_id", "source"])
        self.assertNotIn("self", signature.parameters)
        self.assertNotIn("cls", signature.parameters)

    def test_does_not_contain_engine_terminology(self):
        module = importlib.import_module(
            "manufacturing.door_hinge_engineering_readiness_rule"
        )
        source = inspect.getsource(module)

        self.assertNotIn("HingeRule", source)
        self.assertNotIn("ProjectValidationEngine", source)
        self.assertNotIn("ProjectEngineeringEngine", source)
        self.assertIsNone(re.search(r"\bEngine\b", source))


if __name__ == "__main__":
    unittest.main()
