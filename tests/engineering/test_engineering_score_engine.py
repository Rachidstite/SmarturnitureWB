from validation.intelligence.engineering.engineering_report import (
    EngineeringReport,
)

from validation.intelligence.engineering.engineering_score_engine import (
    EngineeringScoreEngine,
)


def test_score_reduced_by_warnings():

    report = EngineeringReport(
        warnings=[object()],
        errors=[],
    )

    score = (
        EngineeringScoreEngine()
        .calculate(report)
    )

    assert score.score < 100


def test_errors_reduce_score_more():

    report = EngineeringReport(
        warnings=[],
        errors=[object()],
    )

    score = (
        EngineeringScoreEngine()
        .calculate(report)
    )

    assert score.score == 85
