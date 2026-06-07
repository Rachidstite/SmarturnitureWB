from validation.intelligence.manufacturing_rule import (
    ManufacturingRule,
)

from validation.intelligence.rule_result import (
    RuleResult,
)


class MinimumEdgeDistanceRule(
    ManufacturingRule
):

    MIN_DISTANCE = 5.0

    def validate(
        self,
        panel_spec,
        operation
    ):

        distances = [
            operation.x,
            panel_spec.width - operation.x,
            operation.y,
            panel_spec.height - operation.y,
        ]

        if min(distances) < self.MIN_DISTANCE:

            return RuleResult(
                passed=False,
                code="MIN_EDGE_DISTANCE",
                message=(
                    f"Operation too close to edge "
                    f"(< {self.MIN_DISTANCE} mm)"
                )
            )

        return RuleResult(
            passed=True,
            code="OK",
            message="valid"
        )
