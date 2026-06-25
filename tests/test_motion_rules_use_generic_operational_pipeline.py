import importlib
import inspect
import re
import unittest

from project_engineering.motion_envelope_fact import MotionEnvelopeFact
from project_engineering.motion_envelope_overlap_rule import (
    evaluate_motion_envelope_overlap,
)
from project_engineering.operational_decision_from_rule_results import (
    build_operational_decision_from_rule_results,
)


class TestMotionRulesUseGenericOperationalPipeline(unittest.TestCase):
    def test_motion_rule_result_flows_into_generic_operational_decision_pipeline(self):
        moving = MotionEnvelopeFact(
            component_id="MOVING-1",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=10.0,
            y_max=10.0,
            z_max=10.0,
        )
        obstacle = MotionEnvelopeFact(
            component_id="OBSTACLE-1",
            x_min=5.0,
            y_min=5.0,
            z_min=5.0,
            x_max=15.0,
            y_max=15.0,
            z_max=15.0,
        )

        result = evaluate_motion_envelope_overlap(moving, obstacle)
        decision = build_operational_decision_from_rule_results([result])

        self.assertFalse(result.passed)
        self.assertEqual(result.capability, "motion")
        self.assertFalse(decision.ready_for_operation)
        self.assertFalse(decision.ready_for_installation)
        self.assertFalse(decision.ready_for_service)
        self.assertTrue(decision.violations)
        self.assertIn("MOVING-1", decision.violations[0])
        self.assertIn("OBSTACLE-1", decision.violations[0])
        self.assertEqual(decision.warnings, [])

    def test_boundary_source_does_not_contain_engine_or_project_geometry_terms(self):
        module = importlib.import_module(
            "project_engineering.motion_envelope_overlap_rule"
        )
        source = inspect.getsource(module)

        for token in (
            "MotionEngine",
            "MotionDecisionEngine",
            "DoorMotionEngine",
            "DrawerMotionEngine",
            "CollisionEngine",
            "FreeCAD",
            "manufacturing",
            "cost",
            "exports",
            "CNC",
            "scene_graph",
            "project_geometry",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
