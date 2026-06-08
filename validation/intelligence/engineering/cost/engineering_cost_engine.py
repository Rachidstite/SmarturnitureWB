from validation.intelligence.engineering.cost.engineering_cost_impact import (
    EngineeringCostImpact,
)

from validation.intelligence.engineering.cost.cost_registry import (
    COST_IMPACTS,
)


class EngineeringCostEngine:

    def calculate(
        self,
        codes,
    ):

        impacts = []

        for code in codes:

            data = COST_IMPACTS.get(code)

            if not data:
                continue

            impacts.append(
                EngineeringCostImpact(
                    code=code,
                    material_sheets=data["material_sheets"],
                    machining_minutes=data["machining_minutes"],
                    hardware_cost=data["hardware_cost"],
                )
            )

        return impacts
