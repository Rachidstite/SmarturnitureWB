from validation.intelligence.engineering.cost.engineering_cost_summary import (
    EngineeringCostSummary,
)


class EngineeringCostSummaryEngine:

    def summarize(
        self,
        impacts,
    ):

        return EngineeringCostSummary(
            material_sheets=round(
                sum(
                    i.material_sheets
                    for i in impacts
                ),
                2,
            ),
            machining_minutes=sum(
                i.machining_minutes
                for i in impacts
            ),
            hardware_cost=sum(
                i.hardware_cost
                for i in impacts
            ),
        )
