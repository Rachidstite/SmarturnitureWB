from validation.intelligence.unused_operation_cost_impact import (
    UnusedOperationCostImpact,
)


class CostImpactRegistry:

    @staticmethod
    def get_rules():

        return [
            UnusedOperationCostImpact(),
        ]
