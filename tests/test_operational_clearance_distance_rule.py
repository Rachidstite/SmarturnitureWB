import importlib
import inspect
import re
import unittest

from project_engineering.operational_clearance_distance_rule import (
    evaluate_operational_clearance_distance,
)


class TestOperationalClearanceDistanceRule(unittest.TestCase):
    def test_equal_available_and_required_clearance_passes(self):
        result = evaluate_operational_clearance_distance(
            component_id="cabinet-1",
            available_clearance_mm=12.0,
            required_clearance_mm=12.0,
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_greater_available_clearance_passes(self):
        result = evaluate_operational_clearance_distance(
            component_id="cabinet-2",
            available_clearance_mm=15.5,
            required_clearance_mm=10.0,
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_lower_available_clearance_fails(self):
        result = evaluate_operational_clearance_distance(
            component_id="cabinet-3",
            available_clearance_mm=9.0,
            required_clearance_mm=10.0,
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("available=9.0mm", result.message)
        self.assertIn("required=10.0mm", result.message)

    def test_result_stores_identity_fields(self):
        result = evaluate_operational_clearance_distance(
            component_id="cabinet-4",
            available_clearance_mm=7.5,
            required_clearance_mm=8.0,
            capability="serviceability",
            rule_id="RULE-CL-01",
            source="engineering-policy",
        )

        self.assertEqual(result.component_id, "cabinet-4")
        self.assertEqual(result.capability, "serviceability")
        self.assertEqual(result.rule_id, "RULE-CL-01")
        self.assertEqual(result.source, "engineering-policy")

    def test_function_is_generic(self):
        signature = inspect.signature(evaluate_operational_clearance_distance)
        self.assertEqual(
            list(signature.parameters),
            [
                "component_id",
                "available_clearance_mm",
                "required_clearance_mm",
                "capability",
                "rule_id",
                "source",
            ],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.operational_clearance_distance_rule"
        )
        source = inspect.getsource(module)

        self.assertIn("evaluate_operational_clearance_distance", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.operational_clearance_distance_rule"
        )
        source = inspect.getsource(module)

        for token in (
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "FreeCAD",
            "SceneGraph",
            "geometry",
            "operational_capability_contract",
            "operational_decision_from_rule_results",
            "operational_decision_report",
            "cabinet_operational_readiness_report",
            "project_operational_readiness_report",
            "operational_capability_satisfied_rule",
            "motion_contract",
            "accessibility_contract",
            "installation_sequence_contract",
            "serviceability_contract",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_only_allowed_project_engineering_import_is_operational_rule_result(self):
        module = importlib.import_module(
            "project_engineering.operational_clearance_distance_rule"
        )
        source = inspect.getsource(module)

        self.assertIn(
            "from project_engineering.operational_rule_result import OperationalRuleResult",
            source,
        )
        self.assertNotIn("project_engineering.operational_", source.replace(
            "from project_engineering.operational_rule_result import OperationalRuleResult",
            "",
        ))


if __name__ == "__main__":
    unittest.main()
