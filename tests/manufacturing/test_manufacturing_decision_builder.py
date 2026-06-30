import importlib
import inspect
import unittest

from manufacturing.manufacturing_validation_summary_report import (
    ManufacturingValidationSummaryReport,
)
from manufacturing.project_manufacturing_readiness_report import (
    ProjectManufacturingReadinessReport,
)
from project_engineering.project_engineering_readiness_report import (
    ProjectEngineeringReadinessReport,
)


class TestManufacturingDecisionBuilder(unittest.TestCase):
    def setUp(self):
        from manufacturing.manufacturing_decision_builder import (
            ManufacturingDecisionBuilder,
        )

        self.builder = ManufacturingDecisionBuilder()

    def test_pass_when_all_evidence_is_clean(self):
        decision = self.builder.build(
            engineering_readiness_report=self._engineering_ready(),
            manufacturing_validation_summary_report=self._validation_summary(),
            release_validation={"ready": True, "warnings": []},
            project_manufacturing_readiness_report=self._project_readiness("READY"),
        )

        self.assertEqual(decision.status, "PASS")
        self.assertTrue(decision.ready_for_production)
        self.assertEqual(decision.blocking_reasons, ())
        self.assertEqual(decision.warning_reasons, ())
        self.assertEqual(decision.legacy_readiness_status, "READY")
        self.assertEqual(decision.recommended_action, "")

    def test_warning_when_only_warning_evidence_exists(self):
        decision = self.builder.build(
            engineering_readiness_report=self._engineering_ready(),
            manufacturing_validation_summary_report=self._validation_summary(
                warning_count=1,
                warning_messages=["Review manufacturing warning"],
            ),
            release_validation={"ready": True, "warnings": []},
            project_manufacturing_readiness_report=self._project_readiness(
                "REVIEW",
                "Project should be reviewed before production",
            ),
        )

        self.assertEqual(decision.status, "WARNING")
        self.assertFalse(decision.ready_for_production)
        self.assertEqual(decision.blocking_reasons, ())
        self.assertGreaterEqual(len(decision.warning_reasons), 1)
        self.assertEqual(decision.legacy_readiness_status, "REVIEW")
        self.assertNotEqual(decision.recommended_action, "")

    def test_fail_when_engineering_handoff_is_blocked(self):
        decision = self.builder.build(
            engineering_readiness_report=self._engineering_blocked(),
        )

        self.assertEqual(decision.status, "FAIL")
        self.assertFalse(decision.ready_for_production)
        self.assertGreaterEqual(len(decision.blocking_reasons), 1)
        self.assertEqual(decision.legacy_readiness_status, "BLOCKED")

    def test_fail_when_manufacturing_validation_has_blocking_evidence(self):
        decision = self.builder.build(
            engineering_readiness_report=self._engineering_ready(),
            manufacturing_validation_summary_report=self._validation_summary(
                blocking_issue_count=1,
                blocking_messages=["Missing material assignment"],
            ),
        )

        self.assertEqual(decision.status, "FAIL")
        self.assertFalse(decision.ready_for_production)
        self.assertIn("Missing material assignment", decision.blocking_reasons)
        self.assertEqual(decision.legacy_readiness_status, "BLOCKED")

    def test_fail_when_release_validation_blocks_production(self):
        decision = self.builder.build(
            engineering_readiness_report=self._engineering_ready(),
            release_validation={
                "ready": False,
                "warnings": ["No machining operations"],
            },
        )

        self.assertEqual(decision.status, "FAIL")
        self.assertFalse(decision.ready_for_production)
        self.assertIn("No machining operations", decision.blocking_reasons)
        self.assertEqual(decision.legacy_readiness_status, "BLOCKED")

    def test_legacy_readiness_status_maps_correctly(self):
        self.assertEqual(self.builder.build().legacy_readiness_status, "READY")
        self.assertEqual(
            self.builder.build(
                manufacturing_validation_summary_report=self._validation_summary(
                    warning_count=1,
                    warning_messages=["Review me"],
                )
            ).legacy_readiness_status,
            "REVIEW",
        )
        self.assertEqual(
            self.builder.build(
                engineering_readiness_report=self._engineering_blocked()
            ).legacy_readiness_status,
            "BLOCKED",
        )

    def test_ready_for_production_true_only_for_pass(self):
        self.assertTrue(self.builder.build().ready_for_production)
        self.assertFalse(
            self.builder.build(
                manufacturing_validation_summary_report=self._validation_summary(
                    warning_count=1,
                    warning_messages=["Review me"],
                )
            ).ready_for_production
        )
        self.assertFalse(
            self.builder.build(
                engineering_readiness_report=self._engineering_blocked()
            ).ready_for_production
        )

    def test_builder_has_no_banned_imports_or_rule_calls(self):
        module = importlib.import_module("manufacturing.manufacturing_decision_builder")
        source = inspect.getsource(module)

        self.assertIn("ManufacturingDecisionBuilder", source)
        self.assertNotIn("FrontAlignmentRule", source)
        self.assertNotIn("StaticDoorDrawerCollisionRule", source)
        self.assertNotIn("FrontAccessibilityStaticRule", source)
        self.assertNotIn("RevealValidationRule", source)
        self.assertNotIn("StructuralConsistencyRule", source)
        self.assertNotIn("GeometryEngine", source)
        self.assertNotIn("SceneGraph", source)
        self.assertNotIn("Cost", source)
        self.assertNotIn("Optimization", source)
        self.assertNotIn("ManufacturingValidator", source)
        self.assertNotIn("ManufacturingReleaseValidator", source)
        self.assertNotIn("build_manufacturing_validation_report", source)

    @staticmethod
    def _engineering_ready():
        return ProjectEngineeringReadinessReport(
            project_id="PROJECT-1",
            ready_for_engineering_release=True,
            ready_for_manufacturing_handoff=True,
            blocking_violation_count=0,
            warning_count=0,
            source="engineering-readiness-builder",
        )

    @staticmethod
    def _engineering_blocked():
        return ProjectEngineeringReadinessReport(
            project_id="PROJECT-1",
            ready_for_engineering_release=False,
            ready_for_manufacturing_handoff=False,
            blocking_violation_count=1,
            warning_count=0,
            source="engineering-readiness-builder",
        )

    @staticmethod
    def _validation_summary(
        blocking_issue_count=0,
        blocking_messages=(),
        warning_count=0,
        warning_messages=(),
    ):
        return ManufacturingValidationSummaryReport(
            ready_for_manufacturing=(blocking_issue_count == 0),
            total_rule_count=0,
            passed_rule_count=0,
            failed_rule_count=blocking_issue_count + warning_count,
            warning_count=warning_count,
            blocking_issue_count=blocking_issue_count,
            blocking_messages=list(blocking_messages),
            warning_messages=list(warning_messages),
            source="manufacturing-validation-summary-builder",
        )

    @staticmethod
    def _project_readiness(status, recommendation=""):
        return ProjectManufacturingReadinessReport(
            readiness_status=status,
            structural_risk="LOW",
            engineering_review_required=(status != "READY"),
            manufacturing_recommendation=recommendation,
        )


if __name__ == "__main__":
    unittest.main()
