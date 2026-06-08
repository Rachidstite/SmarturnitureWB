from validation.intelligence.unified.unified_dashboard_state import (
    UnifiedDashboardState,
)

from validation.intelligence.unified.unified_dashboard_viewmodel import (
    UnifiedDashboardViewModel,
)


def test_state_exposes_widget_contract():

    vm = UnifiedDashboardViewModel(
        score=90,
        grade="A",
        error_count=0,
        warning_count=1,
        recommendation_count=2,
        recommendations=[
            "r1",
            "r2",
        ],
        can_export=True,
    )

    state = (
        UnifiedDashboardState
        .from_viewmodel(vm)
    )

    assert hasattr(state, "score")
    assert hasattr(state, "grade")
    assert hasattr(state, "warning_count")
    assert hasattr(state, "recommendation_count")
    assert hasattr(state, "recommendations")
    assert hasattr(state, "cost_impact_count")
    assert hasattr(state, "can_export")
