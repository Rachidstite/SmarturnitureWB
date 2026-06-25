from project_engineering.operational_rule_result import OperationalRuleResult


def evaluate_operational_clearance_distance(
    component_id: str,
    available_clearance_mm: float,
    required_clearance_mm: float,
    capability: str = "operational_clearance",
    rule_id: str = "OPERATIONAL_CLEARANCE_DISTANCE",
    source: str = "",
) -> OperationalRuleResult:
    if available_clearance_mm >= required_clearance_mm:
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
        message=(
            "Operational clearance distance is insufficient: "
            f"available={available_clearance_mm}mm, "
            f"required={required_clearance_mm}mm"
        ),
        source=source,
    )
