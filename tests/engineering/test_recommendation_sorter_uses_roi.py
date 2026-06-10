from validation.intelligence.engineering.recommendations.recommendation_sorter import (
    RecommendationSorter,
)

from validation.intelligence.engineering.recommendations.engineering_recommendation import (
    EngineeringRecommendation,
)


def test_same_priority_sorted_by_roi_score():

    recommendations = [

        EngineeringRecommendation(
            title="low roi",
            description="",
            severity="WARNING",
            priority="MEDIUM",
            roi_rating="LOW",
            roi_score=20,
        ),

        EngineeringRecommendation(
            title="high roi",
            description="",
            severity="WARNING",
            priority="MEDIUM",
            roi_rating="EXCELLENT",
            roi_score=95,
        ),
    ]

    result = (
        RecommendationSorter()
        .sort(recommendations)
    )

    assert result[0].roi_score == 95

    assert result[1].roi_score == 20
