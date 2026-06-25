import importlib
import inspect
import re
import unittest

from project_engineering.required_operational_clearance_fact import (
    RequiredOperationalClearanceFact,
)
from project_engineering.required_operational_clearance_fact_extractor import (
    extract_required_operational_clearance_fact,
)


class TestRequiredOperationalClearanceFactExtractor(unittest.TestCase):
    def test_returns_required_operational_clearance_fact(self):
        fact = extract_required_operational_clearance_fact(
            component_id="cabinet-1",
            required_clearance_mm=15.0,
        )

        self.assertIsInstance(fact, RequiredOperationalClearanceFact)

    def test_stores_component_id_and_required_clearance_mm(self):
        fact = extract_required_operational_clearance_fact(
            component_id="cabinet-2",
            required_clearance_mm=17.5,
        )

        self.assertEqual(fact.component_id, "cabinet-2")
        self.assertEqual(fact.required_clearance_mm, 17.5)

    def test_preserves_direction_purpose_and_source(self):
        fact = extract_required_operational_clearance_fact(
            component_id="cabinet-3",
            required_clearance_mm=20.0,
            direction="top",
            purpose="service access",
            source="derived-input",
        )

        self.assertEqual(fact.direction, "top")
        self.assertEqual(fact.purpose, "service access")
        self.assertEqual(fact.source, "derived-input")

    def test_function_signature_remains_generic(self):
        signature = inspect.signature(
            extract_required_operational_clearance_fact
        )
        self.assertEqual(
            list(signature.parameters),
            [
                "component_id",
                "required_clearance_mm",
                "direction",
                "purpose",
                "source",
            ],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.required_operational_clearance_fact_extractor"
        )
        source = inspect.getsource(module)

        for token in (
            "project_geometry",
            "scene_graph",
            "operational_clearance_distance_rule",
            "operational_clearance_facts_rule",
            "operational_rule_result",
            "operational_decision_from_rule_results",
            "operational_decision_report",
            "cabinet_operational_readiness_report",
            "project_operational_readiness_report",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "FreeCAD",
            "CNC",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_does_not_require_component_specific_fields(self):
        fact = extract_required_operational_clearance_fact(
            component_id="cabinet-4",
            required_clearance_mm=9.0,
        )

        self.assertEqual(fact.component_id, "cabinet-4")
        self.assertFalse(hasattr(fact, "door"))
        self.assertFalse(hasattr(fact, "drawer"))
        self.assertFalse(hasattr(fact, "hinge"))
        self.assertFalse(hasattr(fact, "slide"))
        self.assertFalse(hasattr(fact, "shelf"))
        self.assertFalse(hasattr(fact, "panel"))

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.required_operational_clearance_fact_extractor"
        )
        source = inspect.getsource(module)

        self.assertIn("extract_required_operational_clearance_fact", source)
        self.assertNotIn("FreeCAD", source)


if __name__ == "__main__":
    unittest.main()
