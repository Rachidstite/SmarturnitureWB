from manufacturing.manufacturing_validation_report import ManufacturingValidationReport
from manufacturing.manufacturing_validation_summary_report import (
    ManufacturingValidationSummaryReport,
)
from project_engineering.operational_rule_result import OperationalRuleResult


def build_manufacturing_validation_summary_report(
    validation_report: ManufacturingValidationReport,
    rule_results: list[OperationalRuleResult],
) -> ManufacturingValidationSummaryReport:
    blocking_messages = [
        result.message
        for result in rule_results
        if not result.passed and result.severity == "error"
    ]
    warning_messages = [
        result.message for result in rule_results if result.severity == "warning"
    ]

    return ManufacturingValidationSummaryReport(
        ready_for_manufacturing=validation_report.ready_for_manufacturing,
        total_rule_count=validation_report.total_rule_count,
        passed_rule_count=validation_report.passed_rule_count,
        failed_rule_count=validation_report.failed_rule_count,
        warning_count=validation_report.warning_count,
        blocking_issue_count=validation_report.blocking_issue_count,
        blocking_messages=blocking_messages,
        warning_messages=warning_messages,
        source="manufacturing-validation-summary-builder",
    )
