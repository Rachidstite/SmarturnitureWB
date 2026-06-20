from dataclasses import dataclass, field


@dataclass
class ManufacturingComplexityReport:
    complexity_level: str = "LOW"
    complexity_score: int = 0
    engineering_complexity: str = "LOW"
    main_drivers: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
