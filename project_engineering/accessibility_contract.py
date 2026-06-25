from dataclasses import dataclass, field


@dataclass
class AccessibilityRequirement:
    component_id: str
    access_type: str
    access_zone: str
    required_access_mm: float
    purpose: str
    source: str = ""


@dataclass
class AccessibilityReport:
    requirements: list[AccessibilityRequirement] = field(default_factory=list)
    is_satisfied: bool = True
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
