from validation.intelligence.engineering.recommendations.engineering_recommendation_engine import (
    EngineeringRecommendationEngine,
)


def test_recommendation_contains_priority():

    recommendation = (
        EngineeringRecommendationEngine()
        .generate(
            ["EDGE_ERROR"]
        )[0]
    )

    assert recommendation.priority == "CRITICAL"
