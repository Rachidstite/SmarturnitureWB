from validation.intelligence.unified.unified_report import (
    UnifiedReport,
)

from validation.intelligence.unified.unified_score import (
    UnifiedScore,
)

from validation.intelligence.unified.unified_dashboard_viewmodel import (
    UnifiedDashboardViewModel,
)


def test_viewmodel_from_report():

    report = UnifiedReport(
        errors=[object()],
        warnings=[object(), object()],
    )

    report.score = UnifiedScore(
        score=88,
        grade="B",
        explanation="test",
    )

    vm = (
        UnifiedDashboardViewModel
        .from_report(report)
    )

    assert vm.score == 88
    assert vm.grade == "B"
    assert vm.error_count == 1
    assert vm.warning_count == 2
