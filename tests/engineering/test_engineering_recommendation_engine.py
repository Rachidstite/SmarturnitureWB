from validation.intelligence.engineering.recommendations.engineering_recommendation_engine import (
    EngineeringRecommendationEngine,
)


def test_shelf_span_warning_generates_recommendation():

    recommendations = (
        EngineeringRecommendationEngine()
        .generate(
            warning_codes=[
                "SHELF_SPAN_WARNING",
            ]
        )
    )

    assert len(recommendations) == 1

    assert (
        recommendations[0].title
        ==
        "Add Center Divider"
    )
