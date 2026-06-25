import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestRequiredOperationalClearanceFact(unittest.TestCase):
    def test_stores_component_id_and_required_clearance_mm(self):
        from project_engineering.required_operational_clearance_fact import (
            RequiredOperationalClearanceFact,
        )

        fact = RequiredOperationalClearanceFact(
            component_id="cabinet-1",
            required_clearance_mm=10.0,
        )

        self.assertTrue(is_dataclass(RequiredOperationalClearanceFact))
        self.assertEqual(
            [field.name for field in fields(RequiredOperationalClearanceFact)],
            [
                "component_id",
                "required_clearance_mm",
                "direction",
                "purpose",
                "source",
            ],
        )
        self.assertEqual(fact.component_id, "cabinet-1")
        self.assertEqual(fact.required_clearance_mm, 10.0)

    def test_defaults_direction_purpose_and_source_to_empty_strings(self):
        from project_engineering.required_operational_clearance_fact import (
            RequiredOperationalClearanceFact,
        )

        fact = RequiredOperationalClearanceFact(
            component_id="cabinet-2",
            required_clearance_mm=12.5,
        )

        self.assertEqual(fact.direction, "")
        self.assertEqual(fact.purpose, "")
        self.assertEqual(fact.source, "")

    def test_can_store_direction_purpose_and_source(self):
        from project_engineering.required_operational_clearance_fact import (
            RequiredOperationalClearanceFact,
        )

        fact = RequiredOperationalClearanceFact(
            component_id="cabinet-3",
            required_clearance_mm=8.75,
            direction="up",
            purpose="service access",
            source="derived-requirement",
        )

        self.assertEqual(fact.direction, "up")
        self.assertEqual(fact.purpose, "service access")
        self.assertEqual(fact.source, "derived-requirement")

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.required_operational_clearance_fact"
        )
        source = inspect.getsource(module)

        self.assertIn("RequiredOperationalClearanceFact", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.required_operational_clearance_fact"
        )
        source = inspect.getsource(module)

        for token in (
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "FreeCAD",
            "Project Geometry",
            "project_geometry",
            "operational_clearance_distance_rule",
            "operational_rule_result",
            "operational_decision_from_rule_results",
            "operational_decision_report",
            "available_operational_clearance_fact",
            "available_operational_clearance_fact_extractor",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_contract_is_generic_and_component_agnostic(self):
        from project_engineering.required_operational_clearance_fact import (
            RequiredOperationalClearanceFact,
        )

        signature = inspect.signature(RequiredOperationalClearanceFact)
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


if __name__ == "__main__":
    unittest.main()
