from dataclasses import dataclass, field


@dataclass
class AssemblyIntelligenceReport:
    assembly_time_minutes: float = 0.0
    assembly_complexity: str = "LOW"
    required_installers: int = 1
    joinery_density: int = 0
    installation_risk: str = "LOW"
    warnings: list = field(default_factory=list)
