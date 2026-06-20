from dataclasses import dataclass


@dataclass
class HardwareIntelligenceReport:
    hardware_family: str = ""
    total_hardware_items: int = 0
    total_host_holes: int = 0
    total_target_holes: int = 0
    total_face_holes: int = 0
    total_edge_holes: int = 0
    requires_review: bool = False
    manufacturing_warning: str = ""
    recommended_action: str = ""
