from validation.intelligence.unified.unified_report import (
    UnifiedReport,
)

from validation.intelligence.unified.unified_score_engine import (
    UnifiedScoreEngine,
)


def test_warnings_reduce_score():

    report = UnifiedReport(
        warnings=[object()],
        errors=[],
    )

    score = (
        UnifiedScoreEngine()
        .calculate(report)
    )

    assert score.score < 100


def test_errors_reduce_score_more():

    report = UnifiedReport(
        warnings=[],
        errors=[object()],
    )

    score = (
        UnifiedScoreEngine()
        .calculate(report)
    )

    assert score.score <= 70
