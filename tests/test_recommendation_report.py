import unittest

from validation.intelligence.recommended_result import (
    RecommendationResult,
)

from validation.intelligence.recommendation_report import (
    RecommendationReport,
)


class TestRecommendationReport(
    unittest.TestCase
):

    def test_report_stores_recommendations(self):

        report = RecommendationReport(
            recommendations=[
                RecommendationResult(
                    category="SAVINGS",
                    title="Reduce drilling",
                    message="Can remove operation"
                )
            ]
        )

        self.assertEqual(
            len(report.recommendations),
            1
        )


if __name__ == "__main__":
    unittest.main()
