from validation.intelligence.manufacturing_rule import (
    ManufacturingRule,
)

from validation.intelligence.rule_result import (
    RuleResult,
)


class ThroughHoleThicknessRule(
    ManufacturingRule
):

    def validate(
        self,
        panel_spec,
        operation
    ):

        if not operation.is_through:
            return RuleResult(
                passed=True,
                code="OK",
                message="not through hole"
            )

        if operation.depth < panel_spec.thickness:

            return RuleResult(
                passed=False,
                code="THROUGH_HOLE_DEPTH",
                message=(
                    "Through hole depth is smaller "
                    "than panel thickness"
                )
            )

        return RuleResult(
            passed=True,
            code="OK",
            message="valid"
        )
