from validation.intelligence.manufacturing_rule import (
    ManufacturingRule,
)

from validation.intelligence.rule_result import (
    RuleResult,
)

from validation.intelligence.result_level import (
    ResultLevel,
)


class UnusedOperationRule(
    ManufacturingRule
):

    def validate(
        self,
        panel_spec,
        operation
    ):

        intent = operation.metadata.get(
            "hardware_intent"
        )

        if intent:
            return RuleResult(
                passed=True,
                level=ResultLevel.INFO,
                code="USED_OPERATION",
                message="Operation linked to hardware"
            )

        return RuleResult(
            passed=False,
            level=ResultLevel.OPTIMIZATION,
            code="UNUSED_OPERATION",
            message="Operation appears unused"
        )
