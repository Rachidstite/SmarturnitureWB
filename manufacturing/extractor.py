from typing import List
from scene_graph.scene_graph import SceneGraph
from manufacturing.panel_spec import PanelSpec

class ManufacturingExtractor:
    """يحول SceneGraph إلى قائمة PanelSpec جاهزة للتصنيع."""

    @staticmethod
    def extract(scene_graph: SceneGraph) -> List[PanelSpec]:
        specs = []
        for node in scene_graph.all_nodes():
            spec = PanelSpec(
                identity=node.identity.key,
                role=node.role,
                width=node.width,
                height=node.height,
                thickness=node.thickness,
                material=node.material,
                group=node.group,
                edge_spec=node.edge_spec if hasattr(node, 'edge_spec') else None  # ✅ الحواف
            )
            specs.append(spec)
        return specs
