from validation.intelligence.manufacturing_rule import (
    ManufacturingRule,
)

from validation.intelligence.rule_result import (
    RuleResult,
)


class ConnectorIntentRule(
    ManufacturingRule
):

    ALLOWED_INTENTS = {
        "INTENT_MINIFIX_15",
        "INTENT_CONFIRMAT_50",
        "INTENT_HINGE",
        "INTENT_SHELF_PIN",
    }

    def validate(
        self,
        panel_spec,
        operation
    ):

        intent = operation.metadata.get(
            "hardware_intent"
        )

        if intent is None:
            return RuleResult(
                passed=True,
                code="NO_INTENT",
                message="No hardware intent"
            )

        if intent not in self.ALLOWED_INTENTS:
            return RuleResult(
                passed=False,
                code="UNKNOWN_INTENT",
                message=f"Unknown hardware intent: {intent}"
            )

        return RuleResult(
            passed=True,
            code="VALID_INTENT",
            message="Valid hardware intent"
        )
