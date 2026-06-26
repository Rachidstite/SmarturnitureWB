from dataclasses import dataclass


@dataclass
class ManufacturingValidationReport:
    total_rule_count: int = 0
    passed_rule_count: int = 0
    failed_rule_count: int = 0
    warning_count: int = 0
    blocking_issue_count: int = 0
    ready_for_manufacturing: bool = False
    source: str = ""
