from dataclasses import dataclass, field


@dataclass
class InstallationSequenceRequirement:
    component_id: str
    prerequisite_id: str
    sequence_type: str
    reason: str
    purpose: str
    source: str = ""


@dataclass
class InstallationSequenceReport:
    requirements: list[InstallationSequenceRequirement] = field(default_factory=list)
    is_satisfied: bool = True
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
