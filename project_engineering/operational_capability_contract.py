from dataclasses import dataclass, field


@dataclass
class OperationalCapabilityRequirement:
    component_id: str
    capability: str
    purpose: str
    source: str = ""


@dataclass
class OperationalCapabilityReport:
    requirements: list[OperationalCapabilityRequirement] = field(default_factory=list)
    is_satisfied: bool = True
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
