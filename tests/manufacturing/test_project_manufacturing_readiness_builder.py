import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestProjectManufacturingReadinessBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.project_manufacturing_readiness_builder import (
            ProjectManufacturingReadinessBuilder,
        )

        self.builder = ProjectManufacturingReadinessBuilder()

    def test_report_contract(self):
        from manufacturing.project_manufacturing_readiness_report import (
            ProjectManufacturingReadinessReport,
        )

        self.assertTrue(is_dataclass(ProjectManufacturingReadinessReport))
        self.assertEqual(
            [field.name for field in fields(ProjectManufacturingReadinessReport)],
            [
                "readiness_status",
                "structural_risk",
                "engineering_review_required",
                "manufacturing_recommendation",
            ],
        )

        report = ProjectManufacturingReadinessReport()

        self.assertEqual(report.readiness_status, "READY")
        self.assertEqual(report.structural_risk, "LOW")
        self.assertFalse(report.engineering_review_required)
        self.assertEqual(report.manufacturing_recommendation, "")

    def test_any_high_report_blocks_readiness(self):
        report = self.builder.build(
            cabinet_structural_report=self._cabinet_structural_report(structural_risk="HIGH"),
        )

        self.assertEqual(report.readiness_status, "BLOCKED")
        self.assertTrue(report.engineering_review_required)
        self.assertEqual(report.manufacturing_recommendation, "Project manufacturing review required")

    def test_any_medium_report_requires_review(self):
        report = self.builder.build(
            cabinet_stability_report=self._cabinet_stability_report(tipping_risk="MEDIUM"),
        )

        self.assertEqual(report.readiness_status, "REVIEW")
        self.assertFalse(report.engineering_review_required)
        self.assertEqual(
            report.manufacturing_recommendation,
            "Project should be reviewed before production",
        )

    def test_all_low_reports_are_ready(self):
        report = self.builder.build(
            cabinet_structural_report=self._cabinet_structural_report(),
            cabinet_stability_report=self._cabinet_stability_report(),
            hardware_placement_report=self._hardware_placement_report(),
            kitchen_manufacturing_report=self._kitchen_manufacturing_report(),
        )

        self.assertEqual(report.readiness_status, "READY")
        self.assertFalse(report.engineering_review_required)
        self.assertEqual(report.manufacturing_recommendation, "")

    def test_multi_cabinet_project_triggers_review(self):
        report = self.builder.build(
            cabinet_structural_report=self._cabinet_structural_report(),
            cabinet_stability_report=self._cabinet_stability_report(),
            hardware_placement_report=self._hardware_placement_report(),
            kitchen_manufacturing_report=self._kitchen_manufacturing_report(
                cabinet_count=2,
            ),
        )

        self.assertEqual(report.readiness_status, "REVIEW")
        self.assertTrue(report.engineering_review_required)
        self.assertIn(
            "Multi-cabinet project requires installation review",
            report.manufacturing_recommendation,
        )

    def test_multi_cabinet_project_sets_engineering_review_required(self):
        report = self.builder.build(
            cabinet_structural_report=self._cabinet_structural_report(),
            cabinet_stability_report=self._cabinet_stability_report(),
            hardware_placement_report=self._hardware_placement_report(),
            kitchen_manufacturing_report=self._kitchen_manufacturing_report(
                cabinet_count=3,
            ),
        )

        self.assertTrue(report.engineering_review_required)

    def test_existing_blocked_condition_takes_precedence_over_multi_cabinet_review(self):
        report = self.builder.build(
            cabinet_structural_report=self._cabinet_structural_report(structural_risk="HIGH"),
            cabinet_stability_report=self._cabinet_stability_report(),
            hardware_placement_report=self._hardware_placement_report(),
            kitchen_manufacturing_report=self._kitchen_manufacturing_report(
                cabinet_count=2,
            ),
        )

        self.assertEqual(report.readiness_status, "BLOCKED")
        self.assertTrue(report.engineering_review_required)
        self.assertEqual(
            report.manufacturing_recommendation,
            "Project manufacturing review required",
        )

    def test_multi_cabinet_threshold_below_two_preserves_existing_behavior(self):
        report = self.builder.build(
            cabinet_structural_report=self._cabinet_structural_report(),
            cabinet_stability_report=self._cabinet_stability_report(),
            hardware_placement_report=self._hardware_placement_report(),
            kitchen_manufacturing_report=self._kitchen_manufacturing_report(
                cabinet_count=1,
            ),
        )

        self.assertEqual(report.readiness_status, "READY")
        self.assertFalse(report.engineering_review_required)
        self.assertEqual(report.manufacturing_recommendation, "")

    def test_missing_kitchen_manufacturing_report_preserves_existing_behavior(self):
        report = self.builder.build(
            cabinet_structural_report=self._cabinet_structural_report(),
            cabinet_stability_report=self._cabinet_stability_report(),
            hardware_placement_report=self._hardware_placement_report(),
        )

        self.assertEqual(report.readiness_status, "READY")
        self.assertFalse(report.engineering_review_required)
        self.assertEqual(report.manufacturing_recommendation, "")

    def test_blocked_sets_engineering_review_required(self):
        report = self.builder.build(
            hardware_placement_report=self._hardware_placement_report(hardware_risk="HIGH")
        )

        self.assertTrue(report.engineering_review_required)

    def test_recommendation_text_for_review(self):
        report = self.builder.build(
            cabinet_stability_report=self._cabinet_stability_report(large_span_risk="MEDIUM"),
        )

        self.assertEqual(
            report.manufacturing_recommendation,
            "Project should be reviewed before production",
        )

    def test_builder_does_not_mutate_inputs(self):
        cabinet_structural = self._cabinet_structural_report(structural_risk="MEDIUM", tags=["a"])
        cabinet_stability = self._cabinet_stability_report(tipping_risk="MEDIUM", tags=["b"])
        hardware_placement = self._hardware_placement_report(hardware_risk="LOW", tags=["c"])
        kitchen_manufacturing = self._kitchen_manufacturing_report(tags=["d"])

        snapshots = [
            self._snapshot(cabinet_structural),
            self._snapshot(cabinet_stability),
            self._snapshot(hardware_placement),
            self._snapshot(kitchen_manufacturing),
        ]

        self.builder.build(
            cabinet_structural_report=cabinet_structural,
            cabinet_stability_report=cabinet_stability,
            hardware_placement_report=hardware_placement,
            kitchen_manufacturing_report=kitchen_manufacturing,
        )

        self.assertEqual(
            [
                self._snapshot(cabinet_structural),
                self._snapshot(cabinet_stability),
                self._snapshot(hardware_placement),
                self._snapshot(kitchen_manufacturing),
            ],
            snapshots,
        )

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _cabinet_structural_report(structural_risk="LOW", stability_risk="LOW", tags=None):
        return SimpleNamespace(
            structural_risk=structural_risk,
            stability_risk=stability_risk,
            tags=list(tags or []),
        )

    @staticmethod
    def _cabinet_stability_report(tipping_risk="LOW", large_span_risk="LOW", tags=None):
        return SimpleNamespace(
            tipping_risk=tipping_risk,
            large_span_risk=large_span_risk,
            tags=list(tags or []),
        )

    @staticmethod
    def _hardware_placement_report(hardware_risk="LOW", tags=None):
        return SimpleNamespace(
            hardware_risk=hardware_risk,
            tags=list(tags or []),
        )

    @staticmethod
    def _kitchen_manufacturing_report(
        manufacturing_complexity="LOW",
        cabinet_count=0,
        tags=None,
    ):
        return SimpleNamespace(
            manufacturing_complexity=manufacturing_complexity,
            cabinet_count=cabinet_count,
            tags=list(tags or []),
        )


if __name__ == "__main__":
    unittest.main()
