from types import SimpleNamespace

from validation.intelligence.engineering.engineering_score_engine import (
    EngineeringScoreEngine,
)


def test_score_drops_when_warnings_exist():

    report = SimpleNamespace(
        warnings=["w1"],
        errors=[],
    )

    score = (
        EngineeringScoreEngine()
        .calculate(report)
    )

    assert score.score < 100
    assert score.score == 95


def test_errors_penalize_more_than_warnings():

    warning_score = (
        EngineeringScoreEngine()
        .calculate(
            SimpleNamespace(
                warnings=["w1"],
                errors=[],
            )
        )
    )

    error_score = (
        EngineeringScoreEngine()
        .calculate(
            SimpleNamespace(
                warnings=[],
                errors=["e1"],
            )
        )
    )

    assert error_score.score < warning_score.score
