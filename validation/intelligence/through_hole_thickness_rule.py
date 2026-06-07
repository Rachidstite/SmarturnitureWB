from validation.intelligence.manufacturing_rule import (
    ManufacturingRule,
)

from validation.intelligence.rule_result import (
    RuleResult,
)

from validation.intelligence.result_level import (
    ResultLevel,
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
            level=ResultLevel.INFO,
                code="OK",
                message="not through hole"
            )

        if operation.depth < panel_spec.thickness:

            return RuleResult(
                passed=False,
                level=ResultLevel.ERROR,
                code="THROUGH_HOLE_DEPTH",
                message=(
                    "Through hole depth is smaller "
                    "than panel thickness"
                )
            )

        return RuleResult(
            passed=True,
            level=ResultLevel.INFO,
            code="OK",
            message="valid"
        )
