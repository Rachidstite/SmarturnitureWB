from project_engineering.operational_rule_result import OperationalRuleResult


def evaluate_operational_capability_satisfied(
    component_id: str,
    capability: str,
    is_satisfied: bool,
    rule_id: str = "OPERATIONAL_CAPABILITY_SATISFIED",
    source: str = "",
) -> OperationalRuleResult:
    if is_satisfied:
        return OperationalRuleResult(
            rule_id=rule_id,
            capability=capability,
            component_id=component_id,
            passed=True,
            severity="info",
            message="",
            source=source,
        )

    return OperationalRuleResult(
        rule_id=rule_id,
        capability=capability,
        component_id=component_id,
        passed=False,
        severity="error",
        message="Operational capability is not satisfied",
        source=source,
    )
