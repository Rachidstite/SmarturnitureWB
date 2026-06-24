from dataclasses import dataclass


@dataclass
class HardwarePlacementReport:
    placement_quality: str = "UNKNOWN"
    fastener_coverage: str = "UNKNOWN"
    hardware_risk: str = "LOW"
    hardware_recommendation: str = ""
