from validation.intelligence.unified.unified_dashboard_service import (
    UnifiedDashboardService,
)

from validation.intelligence.unified.unified_report import (
    UnifiedReport,
)

from validation.intelligence.unified.unified_score import (
    UnifiedScore,
)


def test_service_builds_result():

    report = UnifiedReport()

    report.score = UnifiedScore(
        score=91,
        grade="A",
        explanation="test",
    )

    result = (
        UnifiedDashboardService()
        .build_from_report(report)
    )

    assert result.viewmodel.score == 91
    assert result.state.score == 91
