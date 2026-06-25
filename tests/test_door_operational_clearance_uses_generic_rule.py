import importlib
import inspect
import re
import unittest

from project_engineering.available_operational_clearance_fact import (
    AvailableOperationalClearanceFact,
)
from project_engineering.door_operational_clearance_requirement import (
    build_door_required_operational_clearance_fact,
)
from project_engineering.operational_clearance_facts_rule import (
    evaluate_operational_clearance_facts,
)


class TestDoorOperationalClearanceUsesGenericRule(unittest.TestCase):
    def test_door_clearance_uses_generic_operational_clearance_facts_rule(self):
        required_fact = build_door_required_operational_clearance_fact(
            door_id="DOOR-1",
            required_clearance_mm=600.0,
            direction="front",
            source="door-test",
        )
        available_fact = AvailableOperationalClearanceFact(
            component_id="DOOR-1",
            available_clearance_mm=420.0,
            direction="front",
            source="geometry-measurement",
        )

        result = evaluate_operational_clearance_facts(
            available_fact,
            required_fact,
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "error")
        self.assertEqual(result.component_id, "DOOR-1")
        self.assertEqual(result.capability, "operational_clearance")
        self.assertIn("available=420.0mm", result.message)
        self.assertIn("required=600.0mm", result.message)
        self.assertEqual(required_fact.purpose, "door operation")

    def test_boundary_source_does_not_require_door_engine_or_validator(self):
        module = importlib.import_module(
            "project_engineering.door_operational_clearance_requirement"
        )
        source = inspect.getsource(module)

        for token in (
            "DoorEngine",
            "DoorClearanceEngine",
            "validator",
            "scene_graph",
            "FreeCAD",
            "manufacturing",
            "cost",
            "exports",
            "CNC",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
