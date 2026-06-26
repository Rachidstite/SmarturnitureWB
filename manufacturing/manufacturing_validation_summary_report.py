from dataclasses import dataclass, field


@dataclass
class ManufacturingValidationSummaryReport:
    ready_for_manufacturing: bool = False
    total_rule_count: int = 0
    passed_rule_count: int = 0
    failed_rule_count: int = 0
    warning_count: int = 0
    blocking_issue_count: int = 0
    blocking_messages: list = field(default_factory=list)
    warning_messages: list = field(default_factory=list)
    source: str = ""
