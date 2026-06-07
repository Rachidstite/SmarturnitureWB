from dataclasses import dataclass


@dataclass
class RuleResult:
    passed: bool
    code: str
    message: str
