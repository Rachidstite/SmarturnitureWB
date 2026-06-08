from dataclasses import dataclass, field


@dataclass
class ManufacturingIntelligenceReport:

    errors: list

    warnings: list

    structural_warnings: list = field(default_factory=list)

    recommendations: list = field(default_factory=list)

    optimizations: list = field(default_factory=list)

    cost_impacts: list = field(default_factory=list)

    score: object = None

    can_export: bool = True
