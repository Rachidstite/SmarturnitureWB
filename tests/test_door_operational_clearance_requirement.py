import importlib
import inspect
import re
import unittest

from project_engineering.door_operational_clearance_requirement import (
    build_door_required_operational_clearance_fact,
)
from project_engineering.required_operational_clearance_fact import (
    RequiredOperationalClearanceFact,
)


class TestDoorOperationalClearanceRequirement(unittest.TestCase):
    def test_returns_required_operational_clearance_fact(self):
        fact = build_door_required_operational_clearance_fact(
            door_id="DOOR-1",
            required_clearance_mm=25.0,
        )

        self.assertIsInstance(fact, RequiredOperationalClearanceFact)

    def test_stores_door_id_as_component_id(self):
        fact = build_door_required_operational_clearance_fact(
            door_id="DOOR-2",
            required_clearance_mm=30.0,
        )

        self.assertEqual(fact.component_id, "DOOR-2")

    def test_preserves_required_clearance_mm(self):
        fact = build_door_required_operational_clearance_fact(
            door_id="DOOR-3",
            required_clearance_mm=32.5,
        )

        self.assertEqual(fact.required_clearance_mm, 32.5)

    def test_defaults_direction_to_front(self):
        fact = build_door_required_operational_clearance_fact(
            door_id="DOOR-4",
            required_clearance_mm=40.0,
        )

        self.assertEqual(fact.direction, "front")

    def test_sets_purpose_to_door_operation(self):
        fact = build_door_required_operational_clearance_fact(
            door_id="DOOR-5",
            required_clearance_mm=18.0,
        )

        self.assertEqual(fact.purpose, "door operation")

    def test_preserves_source(self):
        fact = build_door_required_operational_clearance_fact(
            door_id="DOOR-6",
            required_clearance_mm=18.0,
            source="door-use-case",
        )

        self.assertEqual(fact.source, "door-use-case")

    def test_no_banned_imports(self):
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
            "UI",
            "CNC",
            "OperationalDecisionReport",
            "OperationalRuleResult",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_does_not_create_door_engine_or_validator_terminology(self):
        module = importlib.import_module(
            "project_engineering.door_operational_clearance_requirement"
        )
        source = inspect.getsource(module)

        self.assertNotIn("class DoorEngine", source)
        self.assertNotIn("class DoorClearanceEngine", source)
        self.assertNotIn("validator", source.lower())


if __name__ == "__main__":
    unittest.main()
