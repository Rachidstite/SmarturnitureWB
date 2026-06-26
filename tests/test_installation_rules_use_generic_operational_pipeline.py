import importlib
import inspect
import re
import unittest

from project_engineering.installation_area_fact import InstallationAreaFact
from project_engineering.installation_fit_rule import evaluate_installation_fit
from project_engineering.operational_decision_from_rule_results import (
    build_operational_decision_from_rule_results,
)
from project_engineering.project_footprint import ProjectFootprint


class TestInstallationRulesUseGenericOperationalPipeline(unittest.TestCase):
    def test_installation_fit_flows_through_generic_operational_decision_pipeline(self):
        footprint = ProjectFootprint(
            x_min=0.0,
            y_min=0.0,
            x_max=12.0,
            y_max=12.0,
        )
        installation_area = InstallationAreaFact(
            area_id="AREA-PIPELINE-1",
            x_min=1.0,
            y_min=1.0,
            x_max=10.0,
            y_max=10.0,
        )

        result = evaluate_installation_fit(footprint, installation_area)
        decision = build_operational_decision_from_rule_results([result])

        self.assertFalse(result.passed)
        self.assertEqual(result.capability, "installation_fit")
        self.assertFalse(decision.ready_for_operation)
        self.assertFalse(decision.ready_for_installation)
        self.assertFalse(decision.ready_for_service)
        self.assertEqual(decision.violations, [result.message])
        self.assertEqual(decision.warnings, [])

    def test_installation_fit_rule_module_does_not_depend_on_specialized_engine_layers(self):
        module = importlib.import_module("project_engineering.installation_fit_rule")
        source = inspect.getsource(module)
        source_lower = source.lower()

        for token in (
            "InstallationEngine",
            "InstallationDecisionEngine",
            "RoomEngine",
            "FreeCAD",
            "scene_graph",
            "project_geometry",
            "manufacturing",
            "cost",
            "exports",
            "CNC",
            "pipeline",
            "reducer",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token.lower(), source_lower)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
