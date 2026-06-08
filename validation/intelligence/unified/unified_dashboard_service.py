from validation.intelligence.unified.unified_dashboard_viewmodel import (
    UnifiedDashboardViewModel,
)

from validation.intelligence.unified.unified_dashboard_state import (
    UnifiedDashboardState,
)

from validation.intelligence.unified.unified_dashboard_result import (
    UnifiedDashboardResult,
)


class UnifiedDashboardService:

    def build_from_report(
        self,
        report,
    ):

        viewmodel = (
            UnifiedDashboardViewModel
            .from_report(report)
        )

        state = (
            UnifiedDashboardState
            .from_viewmodel(viewmodel)
        )

        return UnifiedDashboardResult(
            report=report,
            viewmodel=viewmodel,
            state=state,
        )
