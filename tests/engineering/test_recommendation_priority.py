from validation.intelligence.engineering.recommendations.recommendation_priority import (
    RecommendationPriority,
)


def test_edge_error_is_critical():

    assert (
        RecommendationPriority
        .for_code("EDGE_ERROR")
        ==
        "CRITICAL"
    )


def test_shelf_deflection_is_medium():

    assert (
        RecommendationPriority
        .for_code("SHELF_DEFLECTION")
        ==
        "MEDIUM"
    )


def test_unknown_code_defaults_low():

    assert (
        RecommendationPriority
        .for_code("UNKNOWN")
        ==
        "LOW"
    )
