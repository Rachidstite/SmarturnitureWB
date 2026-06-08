from dataclasses import dataclass

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


@dataclass(frozen=True)
class EngineeringResult:

    passed: bool

    level: EngineeringLevel

    code: str

    message: str
