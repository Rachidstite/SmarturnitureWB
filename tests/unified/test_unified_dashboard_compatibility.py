from validation.intelligence.unified.unified_dashboard_viewmodel import (
    UnifiedDashboardViewModel,
)

from validation.intelligence.unified.unified_dashboard_state import (
    UnifiedDashboardState,
)


def test_state_contains_widget_fields():

    vm = UnifiedDashboardViewModel(
        score=95,
        grade="A+",
        error_count=0,
        warning_count=1,
        recommendation_count=2,
        recommendations=[
            "rec1",
            "rec2",
        ],
        can_export=True,
    )

    state = (
        UnifiedDashboardState
        .from_viewmodel(vm)
    )

    assert state.score == 95

    assert state.grade == "A+"

    assert state.warning_count == 1

    assert state.recommendation_count == 2

    assert len(state.recommendations) == 2

    assert state.can_export is True
