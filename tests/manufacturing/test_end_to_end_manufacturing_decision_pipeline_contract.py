import unittest
from types import SimpleNamespace


class TestEndToEndManufacturingDecisionPipelineContract(unittest.TestCase):

    def test_blocked_cabinet_pipeline_flows_into_authority_result(self):
        from cost_intelligence.factory_governance_authority_resolver import (
            FactoryGovernanceAuthorityResolver,
        )
        from cost_intelligence.factory_governance_policy_context import (
            FactoryGovernancePolicyContext,
        )
        from manufacturing.cabinet_engineering_builder import (
            CabinetEngineeringBuilder,
        )
        from manufacturing.cabinet_stability_builder import (
            CabinetStabilityBuilder,
        )
        from manufacturing.cabinet_structural_builder import (
            CabinetStructuralBuilder,
        )
        from manufacturing.manufacturing_authority_result import (
            ManufacturingAuthorityResult,
        )
        from manufacturing.manufacturing_executive_builder import (
            ManufacturingExecutiveBuilder,
        )
        from manufacturing.shelf_structural_report import ShelfStructuralReport

        engineering_builder = CabinetEngineeringBuilder()
        structural_builder = CabinetStructuralBuilder()
        stability_builder = CabinetStabilityBuilder()
        executive_builder = ManufacturingExecutiveBuilder()

        back_panel_report = self._back_panel_intelligence_report()
        shelf_structural_report = ShelfStructuralReport(
            span_risk="HIGH",
            sagging_risk="HIGH",
            support_required=True,
            shelf_recommendation="Shelf support recommended",
        )
        cabinet_engineering_report = engineering_builder.build(
            cabinet_height=2200,
            cabinet_width=1200,
        )
        cabinet_structural_report = structural_builder.build(
            back_panel_report,
            shelf_structural_report=shelf_structural_report,
        )
        cabinet_stability_report = stability_builder.build(
            cabinet_structural_report,
            cabinet_height=2200,
            cabinet_width=1200,
        )

        model_report = SimpleNamespace(manufacturing_status="REVIEW")
        factory_decision_report = SimpleNamespace(
            decision_status="BLOCKED",
            recommendations=[
                cabinet_engineering_report.engineering_recommendation,
                cabinet_structural_report.structural_recommendation,
                cabinet_stability_report.stability_recommendation,
            ],
        )
        executive_intelligence_report = SimpleNamespace(
            delivery_risk="LOW",
            main_bottleneck="",
            priority_action="",
        )
        factory_delivery_report = SimpleNamespace(
            delivery_status="ON_TRACK",
            delivery_recommendation="",
        )
        production_forecast_report = SimpleNamespace(
            forecast_status="ON_SCHEDULE",
            forecast_recommendation="",
        )

        input_snapshot = self._snapshot(
            back_panel_report,
            shelf_structural_report,
            cabinet_engineering_report,
            cabinet_structural_report,
            cabinet_stability_report,
            model_report,
            factory_decision_report,
            executive_intelligence_report,
            factory_delivery_report,
            production_forecast_report,
        )

        executive_report = executive_builder.build(
            model_report,
            factory_decision_report,
            executive_intelligence_report,
            factory_delivery_report,
            production_forecast_report,
        )

        self.assertEqual(executive_report.overall_status, "BLOCKED")

        context = FactoryGovernancePolicyContext(
            readiness_status=executive_report.overall_status,
            profitability_status="LOW",
            capacity_status="OVERLOADED",
            load_status="HIGH",
            risk_status="HIGH",
        )
        context_snapshot = self._snapshot(context)

        authority_report = FactoryGovernanceAuthorityResolver().resolve(context)
        authority_snapshot = self._snapshot(authority_report)

        result = ManufacturingAuthorityResult(
            factory_governance_authority_report=authority_report,
        )

        self.assertIs(result.factory_governance_authority_report, authority_report)
        self.assertEqual(result.factory_governance_authority_report.authority_owner, "ProductionReadinessBuilder")
        self.assertEqual(result.factory_governance_authority_report.authority_rank, 1)
        self.assertEqual(result.factory_governance_authority_report.winning_signal, "READINESS_BLOCKED")
        self.assertIn("LOW_MARGIN", result.factory_governance_authority_report.losing_signals)
        self.assertEqual(
            result.factory_governance_authority_report.explanation,
            "ProductionReadinessBuilder wins because it has the highest authority rank.",
        )
        self.assertEqual(self._snapshot(
            back_panel_report,
            shelf_structural_report,
            cabinet_engineering_report,
            cabinet_structural_report,
            cabinet_stability_report,
            model_report,
            factory_decision_report,
            executive_intelligence_report,
            factory_delivery_report,
            production_forecast_report,
        ), input_snapshot)
        self.assertEqual(self._snapshot(context), context_snapshot)
        self.assertEqual(self._snapshot(authority_report), authority_snapshot)
        self.assertFalse(hasattr(ManufacturingAuthorityResult, "build"))
        self.assertFalse(hasattr(ManufacturingAuthorityResult, "calculate"))
        self.assertFalse(hasattr(ManufacturingAuthorityResult, "compute"))
        self.assertFalse(hasattr(ManufacturingAuthorityResult, "manufacture"))

    @staticmethod
    def _snapshot(*items):
        def freeze(value):
            if isinstance(value, list):
                return [freeze(item) for item in value]
            if isinstance(value, dict):
                return {key: freeze(item) for key, item in value.items()}
            if hasattr(value, "__dict__"):
                return {
                    key: freeze(item)
                    for key, item in value.__dict__.items()
                }
            return value

        return [freeze(item) for item in items]

    @staticmethod
    def _back_panel_intelligence_report():
        back_panel_decision = SimpleNamespace(requires_review=True)
        back_panel_structural = SimpleNamespace(
            structural_risk="HIGH",
            requires_reinforcement=True,
            racking_resistance="LOW",
        )
        return SimpleNamespace(
            decision=back_panel_decision,
            structural=back_panel_structural,
            tags=[],
        )


if __name__ == "__main__":
    unittest.main()
