import importlib
import inspect
import re
import unittest

from project_engineering.available_operational_clearance_fact import (
    AvailableOperationalClearanceFact,
)
from project_engineering.operational_clearance_facts_rule import (
    evaluate_operational_clearance_facts,
)
from project_engineering.required_operational_clearance_fact import (
    RequiredOperationalClearanceFact,
)


class TestOperationalClearanceFactsRule(unittest.TestCase):
    def test_passing_facts_produce_passed_result(self):
        result = evaluate_operational_clearance_facts(
            available_fact=AvailableOperationalClearanceFact(
                component_id="cabinet-1",
                available_clearance_mm=12.0,
            ),
            required_fact=RequiredOperationalClearanceFact(
                component_id="cabinet-1",
                required_clearance_mm=10.0,
            ),
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "")

    def test_failing_facts_produce_failed_result(self):
        result = evaluate_operational_clearance_facts(
            available_fact=AvailableOperationalClearanceFact(
                component_id="cabinet-2",
                available_clearance_mm=8.0,
            ),
            required_fact=RequiredOperationalClearanceFact(
                component_id="cabinet-2",
                required_clearance_mm=10.0,
            ),
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertIn("available=8.0mm", result.message)
        self.assertIn("required=10.0mm", result.message)

    def test_result_uses_available_fact_component_id(self):
        result = evaluate_operational_clearance_facts(
            available_fact=AvailableOperationalClearanceFact(
                component_id="cabinet-3",
                available_clearance_mm=11.0,
            ),
            required_fact=RequiredOperationalClearanceFact(
                component_id="different-component",
                required_clearance_mm=10.0,
            ),
            rule_id="RULE-FACTS-01",
            source="engineering-facts",
        )

        self.assertEqual(result.component_id, "cabinet-3")
        self.assertEqual(result.rule_id, "RULE-FACTS-01")
        self.assertEqual(result.source, "engineering-facts")

    def test_function_has_generic_parameters_only(self):
        signature = inspect.signature(evaluate_operational_clearance_facts)
        self.assertEqual(
            list(signature.parameters),
            ["available_fact", "required_fact", "rule_id", "source"],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.operational_clearance_facts_rule"
        )
        source = inspect.getsource(module)

        self.assertIn("evaluate_operational_clearance_facts", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.operational_clearance_facts_rule"
        )
        source = inspect.getsource(module)

        for token in (
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "FreeCAD",
            "SceneGraph",
            "project_geometry",
            "operational_decision_from_rule_results",
            "operational_decision_report",
            "cabinet_operational_readiness_report",
            "project_operational_readiness_report",
            "operational_capability_satisfied_rule",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_only_allowed_project_engineering_imports(self):
        module = importlib.import_module(
            "project_engineering.operational_clearance_facts_rule"
        )
        source = inspect.getsource(module)

        self.assertIn(
            "from project_engineering.available_operational_clearance_fact import",
            source,
        )
        self.assertIn(
            "from project_engineering.required_operational_clearance_fact import",
            source,
        )
        self.assertIn(
            "from project_engineering.operational_clearance_distance_rule import",
            source,
        )
        self.assertIn(
            "from project_engineering.operational_rule_result import OperationalRuleResult",
            source,
        )

        for token in (
            "project_engineering.operational_decision_from_rule_results",
            "project_engineering.operational_decision_report",
            "project_engineering.cabinet_operational_readiness_report",
            "project_engineering.project_operational_readiness_report",
            "project_engineering.operational_capability_satisfied_rule",
            "project_engineering.motion_contract",
            "project_engineering.accessibility_contract",
            "project_engineering.installation_sequence_contract",
            "project_engineering.serviceability_contract",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
