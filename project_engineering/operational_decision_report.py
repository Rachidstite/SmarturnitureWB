from dataclasses import dataclass, field


@dataclass
class OperationalDecisionReport:
    ready_for_operation: bool = True
    ready_for_installation: bool = True
    ready_for_service: bool = True
    warnings: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
