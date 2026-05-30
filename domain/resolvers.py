from dataclasses import dataclass
from domain.anchors import AnchorCoordinate, EdgeRef, MountFace

@dataclass
class ResolvedAnchor:
    face: str
    local_x: float
    local_y: float

class CoordinateResolver:
    @staticmethod
    def resolve(node, anchor: AnchorCoordinate, hole_offset_x: float = 0.0, hole_offset_y: float = 0.0) -> ResolvedAnchor:
        is_edge_boring = anchor.face in [MountFace.LEFT, MountFace.RIGHT, MountFace.TOP, MountFace.BOTTOM]
        
        # ⚡ Safe Property Extraction (Duck-Typing Resilience)
        width = getattr(node, 'width', 0.0)
        height = getattr(node, 'height', 0.0)
        thickness = getattr(node, 'thickness', 18.0)
        
        # 1. Resolve X Coordinate
        if anchor.edge == EdgeRef.LEFT:
            local_x = anchor.offset_x + hole_offset_x
        elif anchor.edge == EdgeRef.RIGHT:
            local_x = width - anchor.offset_x + hole_offset_x
        elif anchor.edge == EdgeRef.CENTER:
            local_x = (width / 2.0) + anchor.offset_x + hole_offset_x
        elif anchor.edge == EdgeRef.FRONT and is_edge_boring:
            local_x = (thickness / 2.0) + hole_offset_x 
        elif anchor.edge == EdgeRef.BACK and is_edge_boring:
             local_x = (thickness / 2.0) + hole_offset_x
        else:
            local_x = anchor.offset_x + hole_offset_x

        # 2. Resolve Y Coordinate
        if anchor.edge == EdgeRef.BOTTOM:
            local_y = anchor.offset_y + hole_offset_y
        elif anchor.edge == EdgeRef.TOP:
            local_y = height - anchor.offset_y + hole_offset_y
        elif anchor.edge == EdgeRef.CENTER:
            local_y = (height / 2.0) + anchor.offset_y + hole_offset_y
        elif anchor.edge in [EdgeRef.FRONT, EdgeRef.BACK] and is_edge_boring:
             local_y = anchor.offset_y + hole_offset_y
        else:
            local_y = anchor.offset_y + hole_offset_y

        return ResolvedAnchor(
            face=anchor.face.value if hasattr(anchor.face, 'value') else anchor.face,
            local_x=round(local_x, 3),
            local_y=round(local_y, 3)
        )
