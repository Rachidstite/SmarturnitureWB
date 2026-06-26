import importlib
import inspect
import re
import unittest
from types import SimpleNamespace

from project_engineering.project_engineering_readiness_report import (
    ProjectEngineeringReadinessReport,
)


class TestProjectManufacturingReadinessBuilderEngineeringInput(unittest.TestCase):
    def setUp(self):
        from manufacturing.project_manufacturing_readiness_builder import (
            ProjectManufacturingReadinessBuilder,
        )

        self.builder = ProjectManufacturingReadinessBuilder()

    def test_existing_no_input_behavior_remains_unchanged(self):
        report = self.builder.build()

        self.assertEqual(report.readiness_status, "READY")
        self.assertEqual(report.structural_risk, "LOW")
        self.assertFalse(report.engineering_review_required)
        self.assertEqual(report.manufacturing_recommendation, "")

    def test_ready_engineering_readiness_returns_ready(self):
        report = self.builder.build(
            engineering_readiness_report=self._engineering_readiness_report(
                ready_for_manufacturing_handoff=True,
                blocking_violation_count=0,
                warning_count=0,
            )
        )

        self.assertEqual(report.readiness_status, "READY")
        self.assertEqual(report.structural_risk, "LOW")
        self.assertFalse(report.engineering_review_required)
        self.assertIn("engineering handoff ready", report.manufacturing_recommendation)

    def test_blocked_engineering_readiness_returns_blocked(self):
        report = self.builder.build(
            engineering_readiness_report=self._engineering_readiness_report(
                ready_for_manufacturing_handoff=False,
                blocking_violation_count=2,
                warning_count=1,
            )
        )

        self.assertEqual(report.readiness_status, "BLOCKED")
        self.assertEqual(report.structural_risk, "HIGH")
        self.assertTrue(report.engineering_review_required)

    def test_blocked_engineering_readiness_requires_engineering_review(self):
        report = self.builder.build(
            engineering_readiness_report=self._engineering_readiness_report(
                ready_for_manufacturing_handoff=False,
                blocking_violation_count=3,
                warning_count=2,
            )
        )

        self.assertTrue(report.engineering_review_required)

    def test_ready_engineering_readiness_does_not_require_engineering_review(self):
        report = self.builder.build(
            engineering_readiness_report=self._engineering_readiness_report(
                ready_for_manufacturing_handoff=True,
                blocking_violation_count=1,
                warning_count=2,
            )
        )

        self.assertFalse(report.engineering_review_required)

    def test_blocked_recommendation_includes_blocking_violation_count(self):
        report = self.builder.build(
            engineering_readiness_report=self._engineering_readiness_report(
                ready_for_manufacturing_handoff=False,
                blocking_violation_count=4,
                warning_count=0,
            )
        )

        self.assertIn("blocking_violation_count=4", report.manufacturing_recommendation)

    def test_blocked_recommendation_includes_warning_count(self):
        report = self.builder.build(
            engineering_readiness_report=self._engineering_readiness_report(
                ready_for_manufacturing_handoff=False,
                blocking_violation_count=0,
                warning_count=5,
            )
        )

        self.assertIn("warning_count=5", report.manufacturing_recommendation)

    def test_engineering_input_takes_precedence_over_legacy_reports(self):
        report = self.builder.build(
            cabinet_structural_report=SimpleNamespace(structural_risk="HIGH"),
            cabinet_stability_report=SimpleNamespace(tipping_risk="HIGH"),
            hardware_placement_report=SimpleNamespace(hardware_risk="HIGH"),
            kitchen_manufacturing_report=SimpleNamespace(manufacturing_complexity="HIGH"),
            engineering_readiness_report=self._engineering_readiness_report(
                ready_for_manufacturing_handoff=True,
                blocking_violation_count=0,
                warning_count=0,
            ),
        )

        self.assertEqual(report.readiness_status, "READY")
        self.assertEqual(report.structural_risk, "LOW")
        self.assertFalse(report.engineering_review_required)
        self.assertIn("engineering handoff ready", report.manufacturing_recommendation)

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "manufacturing.project_manufacturing_readiness_builder"
        )
        source = inspect.getsource(module)

        self.assertIn("build(", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "manufacturing.project_manufacturing_readiness_builder"
        )
        source = inspect.getsource(module)

        for token in (
            "SceneGraph",
            "CNC",
            "export",
            "cost",
            "nesting",
            "geometry",
            "FurnitureProject",
            "CabinetPlacement",
            "FreeCAD",
            "ProjectManufacturingReadinessBuilderEngine",
            "ProjectValidationEngine",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_function_signature_remains_generic(self):
        from manufacturing.project_manufacturing_readiness_builder import (
            ProjectManufacturingReadinessBuilder,
        )

        signature = inspect.signature(ProjectManufacturingReadinessBuilder.build)
        self.assertEqual(
            list(signature.parameters),
            [
                "self",
                "cabinet_structural_report",
                "cabinet_stability_report",
                "hardware_placement_report",
                "kitchen_manufacturing_report",
                "engineering_readiness_report",
            ],
        )

    def test_does_not_contain_engine_terminology(self):
        module = importlib.import_module(
            "manufacturing.project_manufacturing_readiness_builder"
        )
        source = inspect.getsource(module)

        self.assertIsNone(re.search(r"\bEngine\b", source))
        self.assertNotIn("ProjectManufacturingReadinessBuilderEngine", source)

    def test_existing_report_schema_is_unchanged(self):
        from manufacturing.project_manufacturing_readiness_report import (
            ProjectManufacturingReadinessReport,
        )

        self.assertEqual(
            list(ProjectManufacturingReadinessReport.__dataclass_fields__),
            [
                "readiness_status",
                "structural_risk",
                "engineering_review_required",
                "manufacturing_recommendation",
            ],
        )

    @staticmethod
    def _engineering_readiness_report(
        ready_for_manufacturing_handoff: bool,
        blocking_violation_count: int,
        warning_count: int,
    ):
        return ProjectEngineeringReadinessReport(
            project_id="PROJECT-ENGINEERING",
            ready_for_engineering_release=ready_for_manufacturing_handoff,
            ready_for_manufacturing_handoff=ready_for_manufacturing_handoff,
            blocking_violation_count=blocking_violation_count,
            warning_count=warning_count,
            source="engineering-readiness-builder",
        )


if __name__ == "__main__":
    unittest.main()
