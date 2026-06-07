from dataclasses import dataclass

from validation.intelligence.result_level import (
    ResultLevel,
)


@dataclass
class RuleResult:

    passed: bool

    level: ResultLevel

    code: str

    message: str
