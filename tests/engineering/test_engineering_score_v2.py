from validation.intelligence.engineering.engineering_score_calculator import (
    EngineeringScoreCalculator,
)


def test_perfect_score():

    score = (
        EngineeringScoreCalculator()
        .calculate(
            warnings=[],
            errors=[],
        )
    )

    assert score.score == 100
    assert score.grade == "A+"


def test_warning_reduces_score():

    score = (
        EngineeringScoreCalculator()
        .calculate(
            warnings=["w1"],
            errors=[],
        )
    )

    assert score.score < 100


def test_error_reduces_more_than_warning():

    warning_score = (
        EngineeringScoreCalculator()
        .calculate(
            warnings=["w1"],
            errors=[],
        )
    )

    error_score = (
        EngineeringScoreCalculator()
        .calculate(
            warnings=[],
            errors=["e1"],
        )
    )

    assert error_score.score < warning_score.score


def test_grade_can_drop():

    score = (
        EngineeringScoreCalculator()
        .calculate(
            warnings=["w1","w2","w3"],
            errors=["e1","e2"],
        )
    )

    assert score.grade != "A+"
