from validation.intelligence.manufacturing_rule import (
    ManufacturingRule,
)

from validation.intelligence.rule_result import (
    RuleResult,
)


class MinifixDepthRule(
    ManufacturingRule
):

    REQUIRED_DEPTH = 14

    def validate(
        self,
        panel_spec,
        operation
    ):

        intent = (
            operation.metadata.get(
                "hardware_intent"
            )
        )

        if intent != "INTENT_MINIFIX_15":
            return RuleResult(
                passed=True,
                code="SKIP",
                message="Not a minifix"
            )

        if operation.diameter != 15:
            return RuleResult(
                passed=True,
                code="SKIP",
                message="Not cam drill"
            )

        if operation.depth < self.REQUIRED_DEPTH:
            return RuleResult(
                passed=False,
                code="MINIFIX_DEPTH",
                message="Minifix depth too small"
            )

        return RuleResult(
            passed=True,
            code="OK",
            message="Valid minifix depth"
        )
