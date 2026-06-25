from dataclasses import dataclass


@dataclass
class OperationalRuleResult:
    rule_id: str
    capability: str
    component_id: str
    passed: bool = True
    severity: str = "info"
    message: str = ""
    source: str = ""
