import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestAvailableOperationalClearanceFact(unittest.TestCase):
    def test_stores_component_id_and_clearance(self):
        from project_engineering.available_operational_clearance_fact import (
            AvailableOperationalClearanceFact,
        )

        fact = AvailableOperationalClearanceFact(
            component_id="cabinet-1",
            available_clearance_mm=12.5,
        )

        self.assertTrue(is_dataclass(AvailableOperationalClearanceFact))
        self.assertEqual(
            [field.name for field in fields(AvailableOperationalClearanceFact)],
            [
                "component_id",
                "available_clearance_mm",
                "direction",
                "source",
            ],
        )
        self.assertEqual(fact.component_id, "cabinet-1")
        self.assertEqual(fact.available_clearance_mm, 12.5)

    def test_defaults_direction_and_source_to_empty_strings(self):
        from project_engineering.available_operational_clearance_fact import (
            AvailableOperationalClearanceFact,
        )

        fact = AvailableOperationalClearanceFact(
            component_id="cabinet-2",
            available_clearance_mm=8.0,
        )

        self.assertEqual(fact.direction, "")
        self.assertEqual(fact.source, "")

    def test_can_store_direction_and_source(self):
        from project_engineering.available_operational_clearance_fact import (
            AvailableOperationalClearanceFact,
        )

        fact = AvailableOperationalClearanceFact(
            component_id="cabinet-3",
            available_clearance_mm=7.25,
            direction="left",
            source="derived-from-measurement",
        )

        self.assertEqual(fact.direction, "left")
        self.assertEqual(fact.source, "derived-from-measurement")

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.available_operational_clearance_fact"
        )
        source = inspect.getsource(module)

        self.assertIn("AvailableOperationalClearanceFact", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.available_operational_clearance_fact"
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
            "cabinet_operational_readiness_report",
            "project_operational_readiness_report",
            "operational_capability_satisfied_rule",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_contract_is_generic_and_component_agnostic(self):
        from project_engineering.available_operational_clearance_fact import (
            AvailableOperationalClearanceFact,
        )

        signature = inspect.signature(AvailableOperationalClearanceFact)
        self.assertEqual(
            list(signature.parameters),
            [
                "component_id",
                "available_clearance_mm",
                "direction",
                "source",
            ],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)


if __name__ == "__main__":
    unittest.main()
