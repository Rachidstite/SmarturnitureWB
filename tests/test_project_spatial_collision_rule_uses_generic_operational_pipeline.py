import importlib
import inspect
import re
import unittest

from project_engineering.operational_decision_from_rule_results import (
    build_operational_decision_from_rule_results,
)
from project_engineering.project_spatial_collision_summary_rule import (
    evaluate_project_spatial_collision_summary,
)
from project_engineering.project_spatial_summary_report import (
    ProjectSpatialSummaryReport,
)


class TestProjectSpatialCollisionRuleUsesGenericOperationalPipeline(unittest.TestCase):
    def test_project_spatial_collision_rule_flows_into_generic_operational_decision_pipeline(
        self,
    ):
        report = ProjectSpatialSummaryReport(
            project_id="PROJECT-PIPELINE-1",
            collision_count=2,
            has_collisions=True,
        )

        result = evaluate_project_spatial_collision_summary(report)
        decision = build_operational_decision_from_rule_results([result])

        self.assertFalse(result.passed)
        self.assertEqual(result.capability, "project_spatial_collision")
        self.assertFalse(decision.ready_for_operation)
        self.assertFalse(decision.ready_for_installation)
        self.assertFalse(decision.ready_for_service)
        self.assertTrue(decision.violations)
        self.assertIn("PROJECT-PIPELINE-1", decision.violations[0])
        self.assertIn("collision_count=2", decision.violations[0])
        self.assertEqual(decision.warnings, [])

    def test_boundary_source_does_not_contain_engine_or_geometry_terms(self):
        module = importlib.import_module(
            "project_engineering.project_spatial_collision_summary_rule"
        )
        source = inspect.getsource(module)

        for token in (
            "ProjectEngineeringEngine",
            "ProjectValidationEngine",
            "ProjectOperationalValidationBuilder",
            "Engine",
            "FreeCAD",
            "SceneGraph",
            "manufacturing",
            "cost",
            "exports",
            "CNC",
            "project_geometry",
            "FurnitureProject",
            "CabinetPlacement",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_function_signature_remains_generic(self):
        signature = inspect.signature(evaluate_project_spatial_collision_summary)
        self.assertEqual(list(signature.parameters), ["report", "rule_id", "source"])
        self.assertNotIn("self", signature.parameters)
        self.assertNotIn("cls", signature.parameters)


if __name__ == "__main__":
    unittest.main()
