from dataclasses import dataclass


@dataclass
class FactoryBottleneckIntelligenceReport:
    bottleneck: str = ""
    load_percent: float = 0.0
    severity: str = "LOW"
    impact: str = "NO_MAJOR_BOTTLENECK"
    recommendation: str = "No bottleneck detected"
