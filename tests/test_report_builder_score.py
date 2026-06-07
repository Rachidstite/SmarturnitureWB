import unittest
from unittest.mock import patch

from validation.intelligence.manufacturing_intelligence_report_builder import (
    ManufacturingIntelligenceReportBuilder,
)

from validation.intelligence.manufacturing_score import (
    ManufacturingScore,
)


class TestReportBuilderScore(
    unittest.TestCase
):

    @patch(
        "validation.intelligence.manufacturing_intelligence_report_builder.CostImpactEngine"
    )
    @patch(
        "validation.intelligence.manufacturing_intelligence_report_builder.RecommendationEngine"
    )
    @patch(
        "validation.intelligence.manufacturing_intelligence_report_builder.ManufacturingScoreEngine"
    )
    @patch(
        "validation.intelligence.manufacturing_intelligence_report_builder.ManufacturingRuleEngine"
    )
    def test_builder_calculates_score(
        self,
        rule_engine_cls,
        score_engine_cls,
        recommendation_engine_cls,
        cost_engine_cls
    ):

        rule_engine = rule_engine_cls.return_value
        rule_engine.validate.return_value = []
        rule_engine.errors.return_value = []
        rule_engine.warnings.return_value = []
        rule_engine.optimizations.return_value = []
        rule_engine.can_export.return_value = True

        recommendation_engine_cls.return_value.recommend.return_value = []
        cost_engine_cls.return_value.estimate.return_value = []

        score_engine_cls.return_value.calculate.return_value = (
            ManufacturingScore(
                score=100,
                grade="A",
                explanation="perfect"
            )
        )

        report = (
            ManufacturingIntelligenceReportBuilder()
            .build([])
        )

        self.assertEqual(
            report.score.score,
            100
        )


if __name__ == "__main__":
    unittest.main()
