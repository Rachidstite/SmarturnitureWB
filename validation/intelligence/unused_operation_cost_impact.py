from validation.intelligence.cost_impact import (
    CostImpact,
)

from validation.intelligence.cost_impact_rule import (
    CostImpactRule,
)


class UnusedOperationCostImpact(
    CostImpactRule
):

    def estimate(
        self,
        panel_specs
    ):

        impacts = []

        for panel in panel_specs:

            for op in getattr(
                panel,
                "unified_operations",
                []
            ):

                if not op.metadata.get(
                    "hardware_intent"
                ):
                    impacts.append(
                        CostImpact(
                            category="DRILLING",
                            estimated_savings=1.0,
                            description="Unused operation can be removed"
                        )
                    )

        return impacts
