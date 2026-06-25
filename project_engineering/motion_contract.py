from dataclasses import dataclass, field


@dataclass
class MotionRequirement:
    component_id: str
    motion_type: str
    axis: str
    required_range: float
    unit: str
    purpose: str
    source: str = ""


@dataclass
class MotionReport:
    requirements: list[MotionRequirement] = field(default_factory=list)
    is_satisfied: bool = True
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
