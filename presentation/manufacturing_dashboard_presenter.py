from presentation.manufacturing_dashboard_state import (
    ManufacturingDashboardState,
)


class ManufacturingDashboardPresenter:

    def __init__(self):
        self.state = None

    def set_state(
        self,
        state,
    ):
        self.state = state

    def present(
        self,
        viewmodel,
    ):
        self.state = (
            ManufacturingDashboardState
            .from_viewmodel(viewmodel)
        )

        return self.state
