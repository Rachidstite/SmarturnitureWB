from dataclasses import dataclass
from typing import List
from manufacturing.panel_spec import PanelSpec
from scene_graph.scene_graph import SceneGraph
from manufacturing.extractor import ManufacturingExtractor

@dataclass
class CutListItem:
    identity: str
    width: float
    height: float
    thickness: float
    material: str
    group: str
    role: str
    edge_banding: str = ""
    quantity: int = 1

class CutListEngine:
    @staticmethod
    def extract(scene_graph: SceneGraph) -> List[CutListItem]:
        """يستخرج قائمة القطع من PanelSpecs (طبقة تصنيعية خالصة)."""
        specs = ManufacturingExtractor.extract(scene_graph)
        items = []
        for spec in specs:
            items.append(CutListItem(
                identity=spec.identity,
                width=spec.width,
                height=spec.height,
                thickness=spec.thickness,
                material=spec.material,
                group=spec.group,
                role=spec.role.name if hasattr(spec.role, 'name') else str(spec.role),
                edge_banding=spec.edge_banding,
                quantity=spec.quantity
            ))
        return items
