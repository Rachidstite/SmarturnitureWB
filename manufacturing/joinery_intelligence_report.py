from dataclasses import dataclass, field


@dataclass
class JoineryIntelligenceReport:
    total_minifix: int = 0
    total_hinges: int = 0
    total_drawer_slides: int = 0
    total_handles: int = 0
    total_face_holes: int = 0
    total_edge_holes: int = 0
    total_cam_holes: int = 0
    joinery_complexity_score: int = 0
    warnings: list = field(default_factory=list)
