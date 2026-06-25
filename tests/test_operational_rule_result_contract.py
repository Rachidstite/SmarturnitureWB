import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestOperationalRuleResultContract(unittest.TestCase):

    def test_result_stores_identity_fields(self):
        from project_engineering.operational_rule_result import OperationalRuleResult

        result = OperationalRuleResult(
            rule_id="RULE-1",
            capability="accessibility",
            component_id="COMP-1",
        )

        self.assertTrue(is_dataclass(OperationalRuleResult))
        self.assertEqual(
            [field.name for field in fields(OperationalRuleResult)],
            [
                "rule_id",
                "capability",
                "component_id",
                "passed",
                "severity",
                "message",
                "source",
            ],
        )
        self.assertEqual(result.rule_id, "RULE-1")
        self.assertEqual(result.capability, "accessibility")
        self.assertEqual(result.component_id, "COMP-1")

    def test_default_values(self):
        from project_engineering.operational_rule_result import OperationalRuleResult

        result = OperationalRuleResult(
            rule_id="RULE-1",
            capability="motion",
            component_id="COMP-1",
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")
        self.assertEqual(result.source, "")

    def test_failed_result_can_be_constructed_explicitly(self):
        from project_engineering.operational_rule_result import OperationalRuleResult

        result = OperationalRuleResult(
            rule_id="RULE-2",
            capability="serviceability",
            component_id="COMP-2",
            passed=False,
            severity="error",
            message="rule failed",
            source="ADR-P2",
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertEqual(result.message, "rule failed")
        self.assertEqual(result.source, "ADR-P2")

    def test_contract_is_generic_and_does_not_require_specialized_fields(self):
        from project_engineering.operational_rule_result import OperationalRuleResult

        field_names = [field.name for field in fields(OperationalRuleResult)]

        for token in (
            "door",
            "drawer",
            "hinge",
            "slide",
            "shelf",
            "panel",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, " ".join(field_names).lower())

    def test_module_imports_without_freecad(self):
        module = importlib.import_module("project_engineering.operational_rule_result")

        source = inspect.getsource(module)
        self.assertIn("OperationalRuleResult", source)
        self.assertNotIn("FreeCAD", source)

    def test_module_does_not_import_banned_layers(self):
        module = importlib.import_module("project_engineering.operational_rule_result")

        source = inspect.getsource(module)
        for token in (
            "operational_capability_contract",
            "operational_clearance_contract",
            "motion_contract",
            "accessibility_contract",
            "installation_sequence_contract",
            "serviceability_contract",
            "OperationalDecisionReport",
            "manufacturing",
            "cost",
            "exports",
            "CNC",
            "FreeCAD",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
