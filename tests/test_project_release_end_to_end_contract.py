import unittest
from types import SimpleNamespace
from unittest.mock import patch


class TestProjectReleaseEndToEndContract(unittest.TestCase):

    def test_release_chain_translates_blocked_readiness_to_blocked_decision(self):
        from manufacturing.project_manufacturing_readiness_builder import (
            ProjectManufacturingReadinessBuilder,
        )
        from cost_intelligence.furniture_project_factory_decision_builder import (
            FurnitureProjectFactoryDecisionBuilder,
        )
        from cost_intelligence.factory_decision_report import (
            FactoryDecisionReport,
        )

        structural = self._report(structural_risk="HIGH")
        stability = self._report(tipping_risk="LOW", large_span_risk="LOW")
        hardware = self._report(hardware_risk="LOW")
        kitchen = self._report(manufacturing_complexity="LOW")
        original_structural = self._snapshot(structural)
        original_stability = self._snapshot(stability)
        original_hardware = self._snapshot(hardware)
        original_kitchen = self._snapshot(kitchen)

        readiness = ProjectManufacturingReadinessBuilder().build(
            cabinet_structural_report=structural,
            cabinet_stability_report=stability,
            hardware_placement_report=hardware,
            kitchen_manufacturing_report=kitchen,
        )

        self.assertEqual(readiness.readiness_status, "BLOCKED")
        self.assertTrue(readiness.engineering_review_required)

        furniture_project = SimpleNamespace(
            cabinets=[object()],
            metadata={"name": "Blocked kitchen"},
        )
        original_project = self._snapshot(furniture_project)

        with patch(
            "cost_intelligence.furniture_project_factory_decision_builder."
            "FurnitureProjectManufacturingPackageBuilder"
        ) as project_package_builder_class, patch(
            "cost_intelligence.furniture_project_factory_decision_builder."
            "ManufacturingProductionPackageBuilder"
        ) as production_package_builder_class, patch(
            "cost_intelligence.furniture_project_factory_decision_builder."
            "ManufacturingFactoryIntelligencePipelineBuilder"
        ) as factory_pipeline_builder_class:
            project_package_builder_class.return_value.build.return_value = (
                object()
            )
            production_package_builder_class.return_value.build.return_value = (
                object()
            )
            factory_pipeline_builder_class.return_value.build.return_value = (
                SimpleNamespace(
                    production_readiness_report=SimpleNamespace(
                        status="BLOCKED",
                        manufacturing_ready=False,
                        profitability_ok=True,
                        blocking_issues=["Project readiness blocked"],
                        warnings=["Readiness warning"],
                        recommendations=["Project manufacturing review required"],
                    ),
                    manufacturing_cost_summary=SimpleNamespace(
                        risk_level="LOW",
                        warnings=[],
                        total_manufacturing_cost=0.0,
                        hardware_cost=0.0,
                    ),
                    manufacturing_optimization_result=SimpleNamespace(
                        waste_intelligence_report=SimpleNamespace(
                            risk_level="LOW",
                            warnings=[],
                            recommendation="",
                            waste_cost=0.0,
                            estimated_recovered_value=0.0,
                        ),
                        nesting_intelligence_report=SimpleNamespace(
                            risk_level="LOW",
                            warnings=[],
                            recommendation="",
                        ),
                    ),
                    manufacturing_commercial_result=SimpleNamespace(
                        quotation_intelligence_report=SimpleNamespace(
                            risk_level="LOW",
                            recommendations=[],
                            margin_status="HEALTHY_MARGIN",
                        )
                    ),
                )
            )

            decision_report = (
                FurnitureProjectFactoryDecisionBuilder().build(
                    furniture_project,
                    markup_rate=0.25,
                    currency="MAD",
                )
            )

        self.assertIsInstance(decision_report, FactoryDecisionReport)
        self.assertEqual(decision_report.decision_status, "BLOCKED")
        self.assertIn("Project readiness blocked", decision_report.blocking_issues)

        self.assertEqual(self._snapshot(furniture_project), original_project)
        self.assertEqual(self._snapshot(structural), original_structural)
        self.assertEqual(self._snapshot(stability), original_stability)
        self.assertEqual(self._snapshot(hardware), original_hardware)
        self.assertEqual(self._snapshot(kitchen), original_kitchen)

    def test_manufacturing_release_validator_returns_not_ready_when_warnings_exist(self):
        from manufacturing.manufacturing_package import ManufacturingPackage
        from manufacturing.manufacturing_release_validator import (
            ManufacturingReleaseValidator,
        )

        package = ManufacturingPackage()
        original_package = self._snapshot(package)

        result = ManufacturingReleaseValidator().validate(package)

        self.assertFalse(result["ready"])
        self.assertTrue(result["warnings"])
        self.assertEqual(self._snapshot(package), original_package)

    @staticmethod
    def _report(**kwargs):
        return SimpleNamespace(tags=[], **kwargs)

    @staticmethod
    def _snapshot(obj):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in obj.__dict__.items()
        }


if __name__ == "__main__":
    unittest.main()
