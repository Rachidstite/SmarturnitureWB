from dataclasses import dataclass, field


@dataclass
class UnifiedReport:

    errors: list = field(default_factory=list)

    warnings: list = field(default_factory=list)

    recommendations: list = field(default_factory=list)
