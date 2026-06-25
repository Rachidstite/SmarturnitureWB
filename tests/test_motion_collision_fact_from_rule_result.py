import importlib
import inspect
import re
import unittest

from project_engineering.motion_collision_fact import MotionCollisionFact
from project_engineering.motion_collision_fact_from_rule_result import (
    build_motion_collision_fact_from_rule_result,
)
from project_engineering.operational_rule_result import OperationalRuleResult


class TestMotionCollisionFactFromRuleResult(unittest.TestCase):
    def test_failed_result_builds_collision_fact(self):
        result = OperationalRuleResult(
            rule_id="RULE-1",
            capability="motion",
            component_id="MOV-1",
            passed=False,
            severity="error",
            message="Motion envelopes overlap between MOV-1 and OBS-1",
            source="motion-rule",
        )

        fact = build_motion_collision_fact_from_rule_result(
            result,
            obstacle_component_id="OBS-1",
        )

        self.assertIsInstance(fact, MotionCollisionFact)
        self.assertEqual(fact.moving_component_id, "MOV-1")
        self.assertEqual(fact.obstacle_component_id, "OBS-1")
        self.assertEqual(fact.collision_type, "aabb_overlap")
        self.assertEqual(fact.severity, "error")
        self.assertEqual(fact.message, result.message)
        self.assertEqual(fact.source, "motion-rule")

    def test_uses_result_component_id_as_moving_component_id(self):
        result = OperationalRuleResult(
            rule_id="RULE-2",
            capability="motion",
            component_id="MOV-2",
            passed=False,
            severity="error",
            message="overlap",
            source="src",
        )

        fact = build_motion_collision_fact_from_rule_result(
            result,
            obstacle_component_id="OBS-2",
        )

        self.assertEqual(fact.moving_component_id, "MOV-2")

    def test_uses_provided_obstacle_component_id(self):
        result = OperationalRuleResult(
            rule_id="RULE-3",
            capability="motion",
            component_id="MOV-3",
            passed=False,
            severity="error",
            message="overlap",
            source="src",
        )

        fact = build_motion_collision_fact_from_rule_result(
            result,
            obstacle_component_id="OBS-3",
        )

        self.assertEqual(fact.obstacle_component_id, "OBS-3")

    def test_preserves_collision_type_severity_message_and_source(self):
        result = OperationalRuleResult(
            rule_id="RULE-4",
            capability="motion",
            component_id="MOV-4",
            passed=False,
            severity="warning",
            message="soft overlap",
            source="motion-rule-source",
        )

        fact = build_motion_collision_fact_from_rule_result(
            result,
            obstacle_component_id="OBS-4",
            collision_type="aabb_touch",
        )

        self.assertEqual(fact.collision_type, "aabb_touch")
        self.assertEqual(fact.severity, "warning")
        self.assertEqual(fact.message, "soft overlap")
        self.assertEqual(fact.source, "motion-rule-source")

    def test_passed_result_creates_non_collision_info_fact(self):
        result = OperationalRuleResult(
            rule_id="RULE-5",
            capability="motion",
            component_id="MOV-5",
            passed=True,
            severity="info",
            message="",
            source="motion-rule-source",
        )

        fact = build_motion_collision_fact_from_rule_result(
            result,
            obstacle_component_id="OBS-5",
        )

        self.assertEqual(fact.moving_component_id, "MOV-5")
        self.assertEqual(fact.obstacle_component_id, "OBS-5")
        self.assertEqual(fact.collision_type, "")
        self.assertEqual(fact.severity, "info")
        self.assertEqual(fact.message, "")
        self.assertEqual(fact.source, "motion-rule-source")

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.motion_collision_fact_from_rule_result"
        )
        source = inspect.getsource(module)

        for token in (
            "MotionEngine",
            "CollisionEngine",
            "DoorEngine",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "scene_graph",
            "project_geometry",
            "OperationalDecisionReport",
            "MotionEnvelopeFact",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_no_motion_engine_collision_engine_or_door_engine_terminology(self):
        module = importlib.import_module(
            "project_engineering.motion_collision_fact_from_rule_result"
        )
        source = inspect.getsource(module)

        self.assertNotIn("MotionEngine", source)
        self.assertNotIn("CollisionEngine", source)
        self.assertNotIn("DoorEngine", source)


if __name__ == "__main__":
    unittest.main()
