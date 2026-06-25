import importlib
import inspect
import re
import unittest

from project_engineering.available_operational_clearance_fact import (
    AvailableOperationalClearanceFact,
)
from project_engineering.available_operational_clearance_fact_extractor import (
    extract_available_operational_clearance_fact,
)


class TestAvailableOperationalClearanceFactExtractor(unittest.TestCase):
    def test_extractor_returns_available_operational_clearance_fact(self):
        fact = extract_available_operational_clearance_fact(
            component_id="cabinet-1",
            available_clearance_mm=14.0,
        )

        self.assertIsInstance(fact, AvailableOperationalClearanceFact)

    def test_stores_component_id_and_available_clearance_mm(self):
        fact = extract_available_operational_clearance_fact(
            component_id="cabinet-2",
            available_clearance_mm=11.5,
        )

        self.assertEqual(fact.component_id, "cabinet-2")
        self.assertEqual(fact.available_clearance_mm, 11.5)

    def test_preserves_direction_and_source(self):
        fact = extract_available_operational_clearance_fact(
            component_id="cabinet-3",
            available_clearance_mm=9.25,
            direction="right",
            source="derived-input",
        )

        self.assertEqual(fact.direction, "right")
        self.assertEqual(fact.source, "derived-input")

    def test_function_has_generic_parameters_only(self):
        signature = inspect.signature(
            extract_available_operational_clearance_fact
        )
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

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.available_operational_clearance_fact_extractor"
        )
        source = inspect.getsource(module)

        self.assertIn("extract_available_operational_clearance_fact", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.available_operational_clearance_fact_extractor"
        )
        source = inspect.getsource(module)

        for token in (
            "project_geometry",
            "scene_graph",
            "operational_clearance_distance_rule",
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

    def test_only_allowed_project_engineering_import_is_available_operational_clearance_fact(self):
        module = importlib.import_module(
            "project_engineering.available_operational_clearance_fact_extractor"
        )
        source = inspect.getsource(module)

        self.assertIn(
            "from project_engineering.available_operational_clearance_fact import",
            source,
        )
        self.assertNotIn("project_engineering.operational_", source)


if __name__ == "__main__":
    unittest.main()
