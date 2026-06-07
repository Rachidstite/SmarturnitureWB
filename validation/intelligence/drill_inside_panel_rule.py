from validation.intelligence.manufacturing_rule import (
    ManufacturingRule,
)

from validation.intelligence.rule_result import (
    RuleResult,
)


class DrillInsidePanelRule(
    ManufacturingRule
):

    def validate(
        self,
        panel_spec,
        operation
    ):

        if operation.x is not None:

            if (
                operation.x < 0
                or operation.x > panel_spec.width
            ):
                return RuleResult(
                    passed=False,
                    code="DRILL_OUTSIDE_X",
                    message="Operation outside panel width"
                )

        if operation.y is not None:

            if (
                operation.y < 0
                or operation.y > panel_spec.height
            ):
                return RuleResult(
                    passed=False,
                    code="DRILL_OUTSIDE_Y",
                    message="Operation outside panel height"
                )

        return RuleResult(
            passed=True,
            code="OK",
            message="valid"
        )
