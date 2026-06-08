from validation.intelligence.engineering.recommendations.recommendation_sorter import (
    RecommendationSorter,
)

from validation.intelligence.engineering.recommendations.engineering_recommendation import (
    EngineeringRecommendation,
)


def test_recommendations_sorted_by_priority():

    recommendations = [

        EngineeringRecommendation(
            title="low",
            description="",
            severity="INFO",
            priority="LOW",
        ),

        EngineeringRecommendation(
            title="critical",
            description="",
            severity="ERROR",
            priority="CRITICAL",
        ),

        EngineeringRecommendation(
            title="medium",
            description="",
            severity="WARNING",
            priority="MEDIUM",
        ),
    ]

    sorted_items = (
        RecommendationSorter()
        .sort(recommendations)
    )

    assert sorted_items[0].priority == "CRITICAL"
    assert sorted_items[1].priority == "MEDIUM"
    assert sorted_items[2].priority == "LOW"
