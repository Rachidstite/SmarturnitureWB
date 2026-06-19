import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestFactoryGovernanceCommercialImpactBuilder(unittest.TestCase):

    def _build(
        self,
        primary_recommendation="",
        gross_margin_rate=0.0,
        production_cost=0.0,
        selling_price=0.0,
        gross_profit=0.0,
    ):
        from cost_intelligence.factory_governance_commercial_impact_builder import (
            FactoryGovernanceCommercialImpactBuilder,
        )
        from cost_intelligence.factory_governance_recommendation_report import (
            FactoryGovernanceRecommendationReport,
        )
        from cost_intelligence.profitability_report import ProfitabilityReport
        from cost_intelligence.quotation_report import QuotationReport

        recommendation_report = FactoryGovernanceRecommendationReport(
            primary_recommendation=primary_recommendation
        )
        quotation_report = QuotationReport(
            production_cost=production_cost,
            selling_price=selling_price,
        )
        profitability_report = ProfitabilityReport(
            production_cost=production_cost,
            selling_price=selling_price,
            gross_profit=gross_profit,
            gross_margin_rate=gross_margin_rate,
        )

        return FactoryGovernanceCommercialImpactBuilder().build(
            recommendation_report,
            quotation_report,
            profitability_report,
        )

    def test_report_contract(self):
        from cost_intelligence.factory_governance_commercial_impact_report import (
            FactoryGovernanceCommercialImpactReport,
        )

        self.assertTrue(is_dataclass(FactoryGovernanceCommercialImpactReport))
        self.assertEqual(
            [field.name for field in fields(FactoryGovernanceCommercialImpactReport)],
            [
                "estimated_margin_improvement",
                "estimated_cost_reduction",
                "estimated_profit_increase",
                "impact_confidence",
                "impact_explanation",
            ],
        )
        report = FactoryGovernanceCommercialImpactReport()
        self.assertEqual(report.estimated_margin_improvement, 0.0)
        self.assertEqual(report.estimated_cost_reduction, 0.0)
        self.assertEqual(report.estimated_profit_increase, 0.0)
        self.assertEqual(report.impact_confidence, 0.0)
        self.assertEqual(report.impact_explanation, "")

    def test_every_recommendation_type_produces_impact_output(self):
        cases = [
            ("Review manufacturing constraints", "Readiness recovery"),
            ("Increase quotation price", "Margin recovery opportunity"),
            ("Delay production start", "Schedule improvement"),
            ("Balance workload", "workload"),
            ("Manual engineering review", "Risk reduction opportunity"),
            ("Proceed with production", "No commercial action required"),
        ]
        for recommendation, fragment in cases:
            with self.subTest(recommendation=recommendation):
                report = self._build(
                    primary_recommendation=recommendation,
                    gross_margin_rate=0.08,
                    production_cost=1000.0,
                    selling_price=1100.0,
                    gross_profit=100.0,
                )
                self.assertIsNotNone(report)
                self.assertIn(fragment, report.impact_explanation)

    def test_low_margin_uses_existing_profitability_numbers(self):
        report = self._build(
            primary_recommendation="Increase quotation price",
            gross_margin_rate=0.08,
            production_cost=1000.0,
            selling_price=1100.0,
            gross_profit=100.0,
        )

        self.assertAlmostEqual(report.estimated_margin_improvement, 0.07)
        self.assertAlmostEqual(report.estimated_cost_reduction, 70.0)
        self.assertAlmostEqual(report.estimated_profit_increase, 70.0)
        self.assertGreater(report.impact_confidence, 0.0)

    def test_safe_defaults(self):
        report = self._build()
        self.assertEqual(report.estimated_margin_improvement, 0.0)
        self.assertEqual(report.estimated_cost_reduction, 0.0)
        self.assertEqual(report.estimated_profit_increase, 0.0)
        self.assertEqual(report.impact_confidence, 0.0)
        self.assertEqual(report.impact_explanation, "")

    def test_no_runtime_builder_imports(self):
        from cost_intelligence import factory_governance_commercial_impact_builder

        source = inspect.getsource(factory_governance_commercial_impact_builder)
        forbidden_imports = [
            "FactoryDecisionBuilder",
            "ProductionReadinessBuilder",
            "FactoryDecisionIntelligenceBuilder",
            "ManufacturingExecutiveReportBuilder",
        ]
        for token in forbidden_imports:
            with self.subTest(token=token):
                self.assertNotIn(token, source)

    def test_existing_runtime_behavior_unchanged(self):
        from cost_intelligence.factory_decision_builder import FactoryDecisionBuilder
        from cost_intelligence.factory_decision_intelligence_builder import (
            FactoryDecisionIntelligenceBuilder,
        )
        from cost_intelligence.production_readiness_builder import (
            ProductionReadinessBuilder,
        )

        self.assertNotIn(
            "FactoryGovernanceCommercialImpactBuilder",
            inspect.getsource(FactoryDecisionBuilder),
        )
        self.assertNotIn(
            "FactoryGovernanceCommercialImpactBuilder",
            inspect.getsource(FactoryDecisionIntelligenceBuilder),
        )
        self.assertNotIn(
            "FactoryGovernanceCommercialImpactBuilder",
            inspect.getsource(ProductionReadinessBuilder),
        )
