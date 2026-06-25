from dataclasses import dataclass, field


@dataclass
class ServiceabilityRequirement:
    component_id: str
    service_type: str
    service_zone: str
    required_access_mm: float
    reason: str
    purpose: str
    source: str = ""


@dataclass
class ServiceabilityReport:
    requirements: list[ServiceabilityRequirement] = field(default_factory=list)
    is_satisfied: bool = True
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
