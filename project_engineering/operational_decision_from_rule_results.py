from project_engineering.operational_decision_report import OperationalDecisionReport
from project_engineering.operational_rule_result import OperationalRuleResult


def build_operational_decision_from_rule_results(
    results: list[OperationalRuleResult],
) -> OperationalDecisionReport:
    ready_for_operation = True
    ready_for_installation = True
    ready_for_service = True
    warnings: list[str] = []
    violations: list[str] = []

    for result in results:
        message = result.message.strip()

        if result.passed:
            if result.severity == "warning" and message:
                warnings.append(message)
            continue

        if result.severity == "warning":
            if message:
                warnings.append(message)
            continue

        if message:
            violations.append(message)
        ready_for_operation = False
        ready_for_installation = False
        ready_for_service = False

    return OperationalDecisionReport(
        ready_for_operation=ready_for_operation,
        ready_for_installation=ready_for_installation,
        ready_for_service=ready_for_service,
        warnings=warnings,
        violations=violations,
    )
