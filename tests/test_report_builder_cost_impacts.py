import unittest
from unittest.mock import patch

from validation.intelligence.manufacturing_intelligence_report_builder import (
    ManufacturingIntelligenceReportBuilder,
)


class TestReportBuilderCostImpacts(
    unittest.TestCase
):

    @patch(
        "validation.intelligence.manufacturing_intelligence_report_builder.CostImpactEngine"
    )
    @patch(
        "validation.intelligence.manufacturing_intelligence_report_builder.RecommendationEngine"
    )
    @patch(
        "validation.intelligence.manufacturing_intelligence_report_builder.ManufacturingRuleEngine"
    )
    def test_builder_collects_cost_impacts(
        self,
        rule_engine_cls,
        recommendation_engine_cls,
        cost_engine_cls
    ):

        rule_engine = rule_engine_cls.return_value
        recommendation_engine = recommendation_engine_cls.return_value
        cost_engine = cost_engine_cls.return_value

        rule_engine.validate.return_value = []
        rule_engine.can_export.return_value = True

        recommendation_engine.recommend.return_value = []

        cost_engine.estimate.return_value = [
            "saving"
        ]

        report = (
            ManufacturingIntelligenceReportBuilder()
            .build([])
        )

        self.assertEqual(
            len(report.cost_impacts),
            1
        )


if __name__ == "__main__":
    unittest.main()
