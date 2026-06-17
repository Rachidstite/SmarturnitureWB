import unittest
from dataclasses import fields, is_dataclass


class TestFactoryBottleneckRecommendationReportContract(unittest.TestCase):

    def test_report_is_dataclass_with_exact_field_order(self):
        from manufacturing.factory_bottleneck_recommendation_report import (
            FactoryBottleneckRecommendationReport,
        )

        self.assertTrue(is_dataclass(FactoryBottleneckRecommendationReport))
        self.assertEqual(
            [field.name for field in fields(FactoryBottleneckRecommendationReport)],
            [
                "bottleneck",
                "severity",
                "primary_recommendation",
                "secondary_recommendations",
                "expected_impact",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.factory_bottleneck_recommendation_report import (
            FactoryBottleneckRecommendationReport,
        )

        report = FactoryBottleneckRecommendationReport()

        self.assertEqual(report.bottleneck, "")
        self.assertEqual(report.severity, "LOW")
        self.assertEqual(report.primary_recommendation, "No bottleneck detected")
        self.assertEqual(report.secondary_recommendations, [])
        self.assertEqual(report.expected_impact, "No immediate action required")


if __name__ == "__main__":
    unittest.main()
