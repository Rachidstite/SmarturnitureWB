from validation.intelligence.unified.unified_dashboard_viewmodel import (
    UnifiedDashboardViewModel,
)

from validation.intelligence.unified.unified_dashboard_state import (
    UnifiedDashboardState,
)


def test_state_created_from_viewmodel():

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

    assert state.score == 90
    assert state.grade == "A"
    assert state.error_count == 1
    assert state.warning_count == 2
    assert state.recommendation_count == 3
