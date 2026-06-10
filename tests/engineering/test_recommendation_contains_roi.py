from validation.intelligence.engineering.recommendations.engineering_recommendation_engine import (
    EngineeringRecommendationEngine,
)


def test_recommendation_contains_roi():

    recommendation = (
        EngineeringRecommendationEngine()
        .generate(
            ["SHELF_DEFLECTION"]
        )[0]
    )

    assert recommendation.roi_rating == "EXCELLENT"

    assert recommendation.roi_score >= 90
