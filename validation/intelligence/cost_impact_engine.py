from validation.intelligence.cost_impact_registry import (
    CostImpactRegistry,
)


class CostImpactEngine:

    def estimate(
        self,
        panel_specs
    ):

        impacts = []

        for rule in (
            CostImpactRegistry
            .get_rules()
        ):

            impacts.extend(
                rule.estimate(
                    panel_specs
                )
            )

        return impacts
