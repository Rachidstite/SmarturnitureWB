import unittest
from unittest.mock import patch

from validation.intelligence.manufacturing_intelligence_report_builder import (
    ManufacturingIntelligenceReportBuilder,
)


class TestManufacturingIntelligenceReportBuilder(
    unittest.TestCase
):

    @patch(
        "validation.intelligence.manufacturing_intelligence_report_builder.RecommendationEngine"
    )
    @patch(
        "validation.intelligence.manufacturing_intelligence_report_builder.ManufacturingRuleEngine"
    )
    def test_build_report(
        self,
        rule_engine_cls,
        recommendation_engine_cls
    ):

        rule_engine = (
            rule_engine_cls.return_value
        )

        recommendation_engine = (
            recommendation_engine_cls.return_value
        )

        rule_engine.errors.return_value = []
        rule_engine.warnings.return_value = []
        rule_engine.optimizations.return_value = []
        rule_engine.can_export.return_value = True

        recommendation_engine.recommend.return_value = []

        report = (
            ManufacturingIntelligenceReportBuilder()
            .build([])
        )

        self.assertTrue(
            report.can_export
        )


if __name__ == "__main__":
    unittest.main()
