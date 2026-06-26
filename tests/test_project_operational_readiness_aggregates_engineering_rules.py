import inspect
import re
import unittest

from project_engineering.installation_fit_rule import evaluate_installation_fit
from project_engineering.installation_area_fact import InstallationAreaFact
from project_engineering.operational_decision_from_rule_results import (
    build_operational_decision_from_rule_results,
)
from project_engineering.operational_rule_result import OperationalRuleResult
from project_engineering.project_footprint import ProjectFootprint


class TestProjectOperationalReadinessAggregatesEngineeringRules(unittest.TestCase):
    def test_project_level_readiness_uses_generic_operational_reducer(self):
        installation_result = OperationalRuleResult(
            rule_id="INSTALLATION_FIT",
            capability="installation_fit",
            component_id="AREA-1",
            passed=True,
            severity="info",
            message="",
            source="installation-fit",
        )
        motion_result = OperationalRuleResult(
            rule_id="MOTION_OVERLAP",
            capability="motion",
            component_id="CABINET-1",
            passed=False,
            severity="error",
            message="motion failure blocks project readiness",
            source="motion-rule",
        )
        clearance_result = OperationalRuleResult(
            rule_id="OPERATIONAL_CLEARANCE",
            capability="operational_clearance",
            component_id="CABINET-1",
            passed=False,
            severity="warning",
            message="operational clearance requires review",
            source="clearance-rule",
        )

        decision = build_operational_decision_from_rule_results(
            [installation_result, motion_result, clearance_result]
        )

        self.assertTrue(installation_result.passed)
        self.assertFalse(decision.ready_for_operation)
        self.assertFalse(decision.ready_for_installation)
        self.assertFalse(decision.ready_for_service)
        self.assertIn("motion failure blocks project readiness", decision.violations)
        self.assertIn("operational clearance requires review", decision.warnings)

    def test_installation_fit_rule_can_participate_in_generic_readiness_pipeline(self):
        footprint = ProjectFootprint(
            x_min=0.0,
            y_min=0.0,
            x_max=12.0,
            y_max=12.0,
        )
        installation_area = InstallationAreaFact(
            area_id="AREA-PIPELINE",
            x_min=1.0,
            y_min=1.0,
            x_max=10.0,
            y_max=10.0,
        )

        installation_result = evaluate_installation_fit(footprint, installation_area)
        self.assertFalse(installation_result.passed)
        self.assertEqual(installation_result.capability, "installation_fit")

        motion_result = OperationalRuleResult(
            rule_id="MOTION_OVERLAP",
            capability="motion",
            component_id="CABINET-1",
            passed=False,
            severity="error",
            message="motion failure blocks project readiness",
        )
        clearance_result = OperationalRuleResult(
            rule_id="OPERATIONAL_CLEARANCE",
            capability="operational_clearance",
            component_id="CABINET-1",
            passed=False,
            severity="warning",
            message="operational clearance requires review",
        )

        decision = build_operational_decision_from_rule_results(
            [installation_result, motion_result, clearance_result]
        )

        self.assertFalse(decision.ready_for_operation)
        self.assertFalse(decision.ready_for_installation)
        self.assertFalse(decision.ready_for_service)
        self.assertIn("motion failure blocks project readiness", decision.violations)
        self.assertIn("operational clearance requires review", decision.warnings)

    def test_relevant_project_engineering_modules_do_not_define_specialized_readiness_engines(self):
        import project_engineering.cabinet_operational_readiness_report as cabinet_report_module
        import project_engineering.installation_fit_rule as installation_fit_module
        import project_engineering.operational_decision_from_rule_results as decision_module
        import project_engineering.project_operational_readiness_report as project_report_module

        source = "\n".join(
            inspect.getsource(module)
            for module in (
                installation_fit_module,
                decision_module,
                project_report_module,
                cabinet_report_module,
            )
        )

        for token in (
            "ProjectEngineeringEngine",
            "ProjectReadinessEngine",
            "InstallationEngine",
            "MotionEngine",
            "ClearanceEngine",
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
