from manufacturing.manufacturing_validation_report import (
    ManufacturingValidationReport,
)
from project_engineering.operational_rule_result import OperationalRuleResult


def build_manufacturing_validation_report(
    rule_results: list[OperationalRuleResult],
) -> ManufacturingValidationReport:
    total_rule_count = len(rule_results)
    passed_rule_count = sum(1 for result in rule_results if result.passed)
    failed_rule_count = total_rule_count - passed_rule_count
    warning_count = sum(1 for result in rule_results if result.severity == "warning")
    blocking_issue_count = sum(
        1 for result in rule_results if (not result.passed and result.severity == "error")
    )

    return ManufacturingValidationReport(
        total_rule_count=total_rule_count,
        passed_rule_count=passed_rule_count,
        failed_rule_count=failed_rule_count,
        warning_count=warning_count,
        blocking_issue_count=blocking_issue_count,
        ready_for_manufacturing=blocking_issue_count == 0,
        source="manufacturing-validation-builder",
    )
