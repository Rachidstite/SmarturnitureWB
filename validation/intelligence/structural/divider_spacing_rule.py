from validation.intelligence.manufacturing_rule import (
    ManufacturingRule,
)

from validation.intelligence.rule_result import (
    RuleResult,
)

from validation.intelligence.result_level import (
    ResultLevel,
)

from shared.roles import NodeRole


class DividerSpacingRule(
    ManufacturingRule
):

    MAX_OPENING = 1200.0

    def validate(
        self,
        panel_spec,
        operation
    ):

        if panel_spec.role != NodeRole.SHELF:
            return RuleResult(
                passed=True,
                level=ResultLevel.INFO,
                code="SKIP",
                message="Not shelf"
            )

        span = getattr(
            panel_spec,
            "span",
            panel_spec.width
        )

        if span > self.MAX_OPENING:

            return RuleResult(
                passed=False,
                level=ResultLevel.WARNING,
                code="DIVIDER_RECOMMENDED",
                message=(
                    f"Opening {span:.0f} mm "
                    f"should include divider"
                )
            )

        return RuleResult(
            passed=True,
            level=ResultLevel.INFO,
            code="OK",
            message="Divider not required"
        )
