from validation.intelligence.manufacturing_rule import (
    ManufacturingRule,
)

from validation.intelligence.rule_result import (
    RuleResult,
)


class ConfirmatDepthRule(
    ManufacturingRule
):

    REQUIRED_DEPTH = 12

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

        if (
            intent !=
            "INTENT_CONFIRMAT_50"
        ):
            return RuleResult(
                passed=True,
                code="SKIP",
                message="Not confirmat"
            )

        if (
            operation.depth <
            self.REQUIRED_DEPTH
        ):
            return RuleResult(
                passed=False,
                code="CONFIRMAT_DEPTH",
                message="Confirmat depth too small"
            )

        return RuleResult(
            passed=True,
            code="OK",
            message="Valid confirmat depth"
        )
