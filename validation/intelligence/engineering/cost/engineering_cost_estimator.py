class EngineeringCostEstimator:

    MDF_SHEET_COST = 800

    MACHINING_MINUTE_COST = 2

    def estimate(
        self,
        summary,
    ):

        return (
            summary.material_sheets
            * self.MDF_SHEET_COST
        ) + (
            summary.machining_minutes
            * self.MACHINING_MINUTE_COST
        ) + (
            summary.hardware_cost
        )
