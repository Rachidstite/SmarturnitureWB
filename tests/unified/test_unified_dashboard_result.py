from validation.intelligence.unified.unified_dashboard_result import (
    UnifiedDashboardResult,
)

from validation.intelligence.unified.unified_report import (
    UnifiedReport,
)

from validation.intelligence.unified.unified_dashboard_viewmodel import (
    UnifiedDashboardViewModel,
)

from validation.intelligence.unified.unified_dashboard_state import (
    UnifiedDashboardState,
)


def test_result_holds_objects():

    report = UnifiedReport()

    vm = UnifiedDashboardViewModel(
        score=90,
        grade="A",
        error_count=1,
        warning_count=2,
        recommendation_count=3,
    )

    state = (
        UnifiedDashboardState
        .from_viewmodel(vm)
    )

    result = UnifiedDashboardResult(
        report=report,
        viewmodel=vm,
        state=state,
    )

    assert result.report is report
    assert result.viewmodel is vm
    assert result.state is state
