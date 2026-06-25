from dataclasses import dataclass, field


@dataclass
class OperationalClearanceRequirement:
    component_id: str
    required_clearance_mm: float
    direction: str
    purpose: str
    source: str = ""


@dataclass
class OperationalClearanceReport:
    requirements: list[OperationalClearanceRequirement] = field(default_factory=list)
    is_satisfied: bool = True
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
